import datetime
import fcntl
import logging
import os
import pkg_resources
import pty
import re
import selectors
import struct
import termios
import tty
from collections import namedtuple
from copy import copy
from functools import partial
from typing import Any, Callable, Dict, Generator, Iterable, Iterator, Tuple, Union

import pyte
import pyte.screens
from Xlib import display, rdb, Xatom
from Xlib.error import DisplayError

from termtosvg.anim import CharacterCellConfig, CharacterCellLineEvent, CharacterCellRecord

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

XRESOURCES_DIR = os.path.join('data', 'Xresources')

# asciicast v2 record formats
# Full specification: https://github.com/asciinema/asciinema/blob/develop/doc/asciicast-v2.md
AsciiCastHeader = namedtuple('AsciiCastHeader', ['version', 'width', 'height', 'theme'])
AsciiCastHeader.__doc__ = """Header record"""
AsciiCastHeader.version.__doc__ = """Version of the asciicast file format"""
AsciiCastHeader.width.__doc__ = """Initial number of columns of the terminal"""
AsciiCastHeader.height.__doc__ = """Initial number of lines of the terminal"""
AsciiCastHeader.theme.__doc__ = """Color theme of the terminal"""

AsciiCastTheme = namedtuple('AsciiCastTheme', ['fg', 'bg', 'palette'])
AsciiCastTheme.__doc__ = """Color theme of the terminal. All colors must use the '#rrggbb' format"""
AsciiCastTheme.fg.__doc__ = """Default text color"""
AsciiCastTheme.bg.__doc__ = """Default background color"""
AsciiCastTheme.palette.__doc__ = """Colon separated list of the 8 or 16 terminal colors"""

AsciiCastEvent = namedtuple('AsciiCastEvent', ['time', 'event_type', 'event_data', 'duration'])
AsciiCastEvent.__doc__ = """Event record"""
AsciiCastEvent.time.__doc__ = """Time elapsed since the beginning of the recording in seconds"""
AsciiCastEvent.event_type.__doc__ = """Type 'o' if the data was captured on the standard """ \
                                    """output of the terminal, type 'i' if it was captured on """ \
                                    """the standard input"""
AsciiCastEvent.event_data.__doc__ = """Data captured during the recording"""
AsciiCastEvent.duration.__doc__ = """Duration of the event in seconds (non standard field)"""

AsciiCastRecord = Union[AsciiCastHeader, AsciiCastEvent]


class TerminalMode:
    """Save terminal state on entry, restore it on exit"""
    def __init__(self, fileno: int):
        self.fileno = fileno
        self.mode = None

    def __enter__(self):
        try:
            self.mode = tty.tcgetattr(self.fileno)
        except tty.error:
            pass
        return self.mode

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mode is not None:
            tty.tcsetattr(self.fileno, tty.TCSAFLUSH, self.mode)


def record(columns, lines, theme, input_fileno, output_fileno):
    # type: (int, int, AsciiCastTheme, int, int) -> Generator[AsciiCastRecord, None, None]
    """Record a terminal session in asciicast v2 format

    The records returned are of two types:
        - a single header with configuration information
        - multiple event records with data captured from the terminal and timing information
    """
    yield AsciiCastHeader(version=2, width=columns, height=lines, theme=theme)

    start = None
    for data, time in _record(columns, lines, input_fileno, output_fileno):
        if start is None:
            start = time

        yield AsciiCastEvent(time=(time - start).total_seconds(),
                             event_type='o',
                             event_data=data,
                             duration=None)


def _record(columns, lines, input_fileno, output_fileno):
    # type: (int, int, int, int) -> Generator[Tuple[bytes, datetime.datetime], None, int]
    """Record raw input and output of a shell session

    This function forks the current process. The child process is a shell which is a session
    leader and has a controlling terminal and is run in the background. The parent process, which
    runs in the foreground, transmits data between the standard input, output and the shell
    process and logs it. From the user point of view, it appears they are communicating with
    their shell (through their terminal emulator) when in fact they communicate with our parent
    process which logs all the data exchanged with the shell

    The implementation of this method is mostly copied from the pty.spawn function of the
    CPython standard library. It has been modified in order to make the record function a
    generator.
    See https://github.com/python/cpython/blob/master/Lib/pty.py

    :param columns: Initial number of columns of the terminal
    :param lines: Initial number of lines of the terminal
    :param input_fileno: File descriptor of the input data stream
    :param output_fileno: File descriptor of the output data stream
    """
    shell = os.environ.get('SHELL', 'sh')

    pid, master_fd = pty.fork()
    if pid == 0:
        # Child process
        os.execlp(shell, shell)

    # Set the terminal size for master_fd
    ttysize = struct.pack("HHHH", lines, columns, 0, 0)
    fcntl.ioctl(master_fd, termios.TIOCSWINSZ, ttysize)

    # Parent process
    try:
        tty.setraw(input_fileno)
    except tty.error:
        pass

    for data, time in _capture_data(input_fileno, output_fileno, master_fd):
        yield data, time

    os.close(master_fd)

    _, child_exit_status = os.waitpid(pid, 0)
    return child_exit_status


def _capture_data(input_fileno, output_fileno, master_fd, buffer_size=1024):
    # type: (int, int, int, int) -> Generator[bytes, datetime.datetime]
    """Send data from input_fileno to master_fd and send data from master_fd to output_fileno and
    also return it to the caller

    The implementation of this method is mostly copied from the pty.spawn function of the
    CPython standard library. It has been modified in order to make the record function a
    generator.
    See https://github.com/python/cpython/blob/master/Lib/pty.py
    """
    sel = selectors.DefaultSelector()
    sel.register(master_fd, selectors.EVENT_READ)
    sel.register(input_fileno, selectors.EVENT_READ)

    while {master_fd, input_fileno} <= set(sel.get_map()):
        events = sel.select()
        for key, _ in events:
            try:
                data = os.read(key.fileobj, buffer_size)
            except OSError:
                sel.unregister(key.fileobj)
                continue

            if not data:
                sel.unregister(key.fileobj)
                continue

            if key.fileobj == input_fileno:
                write_fileno = master_fd
            else:
                write_fileno = output_fileno
                yield data, datetime.datetime.now()

            while data:
                n = os.write(write_fileno, data)
                data = data[n:]


def _group_by_time(event_records, min_rec_duration, last_rec_duration):
    # type: (Iterable[AsciiCastEvent], float, float) -> Generator[AsciiCastEvent, None, None]
    """Merge event records together if they are close enough and compute the duration between
    consecutive events. The duration between two consecutive event records returned by the function
    is guaranteed to be at least min_rec_duration.

    :param event_records: Sequence of records in asciicast v2 format
    :param min_rec_duration: Minimum time between two records returned by the function in seconds
    :param last_rec_duration: Duration of the last record in seconds
    :return: Sequence of records
    """
    current_string = b''
    current_time = None

    for event_record in event_records:
        if event_record.event_type != 'o':
            continue

        if current_time is not None:
            time_between_events = event_record.time - current_time
            if time_between_events >= min_rec_duration:
                accumulator_event = AsciiCastEvent(time=current_time,
                                                   event_type='o',
                                                   event_data=current_string,
                                                   duration=time_between_events)
                yield accumulator_event
                current_string = b''
                current_time = event_record.time
        else:
            current_time = event_record.time

        current_string += event_record.event_data

    if current_string:
        accumulator_event = AsciiCastEvent(time=current_time,
                                           event_type='o',
                                           event_data=current_string,
                                           duration=last_rec_duration)
        yield accumulator_event


def replay(records, from_pyte_char, min_frame_duration=0, last_frame_duration=1):
    # type: (Iterable[AsciiCastRecord], Callable[[pyte.screen.Char, Dict[Any, str]], Any], float, float) -> Generator[CharacterCellRecord, None, None]
    """Read the records of a terminal sessions, render the corresponding screens and return lines
    of the screen that need updating.

    Records are merged together so that there is at least a 'min_frame_duration' seconds pause
    between two rendered screens.
    Lines returned are sorted by time and duration of their appearance on the screen so that lines
    in need of updating at the same time can easily be grouped together.
    The terminal screen is rendered using Pyte and then each character of the screen is converted
    to the caller's format of choice using from_pyte_char

    :param records: Records of the terminal session in asciicast v2 format. The first record must
    be a header, which must be followed by event records.
    :param from_pyte_char: Conversion function from pyte.screen.Char to any other format
    :param min_frame_duration: Minimum frame duration in seconds
    :param last_frame_duration: Last frame duration in seconds
    :return: Records in the CharacterCellRecord format:
        1/ a header with configuration information (CharacterCellConfig)
        2/ one event record for each line of the screen that need to be redrawn (CharacterCellLineEvent)
    """
    def sort_by_time(d, row):
        row_line, row_line_time, row_line_duration = d[row]
        return row_line_time + row_line_duration, row

    if not isinstance(records, Iterator):
        records = iter(records)

    header = next(records)
    screen = pyte.Screen(header.width, header.height)
    stream = pyte.ByteStream(screen)

    config = CharacterCellConfig(width=header.width,
                                 height=header.height,
                                 text_color=header.theme.fg,
                                 background_color=header.theme.bg)
    yield config

    palette = {
        'foreground': header.theme.fg,
        'background': header.theme.bg
    }
    palette.update(enumerate(header.theme.palette.split(':')))

    pending_lines = {}
    current_time = 0
    last_cursor = None
    for event_record in _group_by_time(records, min_frame_duration, last_frame_duration):
        stream.feed(event_record.event_data)

        # Numbers of lines that must be redrawn
        dirty_lines = set(screen.dirty)
        if screen.cursor != last_cursor:
            # Line where the cursor will be drawn
            dirty_lines.add(screen.cursor.y)
            if last_cursor is not None:
                # Line where the cursor will be erased
                dirty_lines.add(last_cursor.y)

        redraw_buffer = {}
        for row in dirty_lines:
            redraw_buffer[row] = {}
            for column in screen.buffer[row]:
                redraw_buffer[row][column] = from_pyte_char(screen.buffer[row][column], palette)

        if screen.cursor != last_cursor:
            try:
                data = screen.buffer[screen.cursor.y][screen.cursor.x].data
            except KeyError:
                data = ' '

            cursor_char = pyte.screens.Char(data=data,
                                            fg=screen.cursor.attrs.fg,
                                            bg=screen.cursor.attrs.bg,
                                            reverse=True)
            redraw_buffer[screen.cursor.y][screen.cursor.x] = from_pyte_char(cursor_char, palette)

        last_cursor = copy(screen.cursor)
        screen.dirty.clear()

        completed_lines = {}
        # Conversion from seconds to milliseconds
        duration = int(1000 * round(event_record.duration, 3))
        for row in pending_lines:
            line, line_time, line_duration = pending_lines[row]
            if row in redraw_buffer:
                completed_lines[row] = line, line_time, line_duration
            else:
                pending_lines[row] = line, line_time, line_duration + duration

        for row in redraw_buffer:
            if redraw_buffer[row]:
                pending_lines[row] = redraw_buffer[row], current_time, duration
            elif row in pending_lines:
                del pending_lines[row]

        for row in sorted(completed_lines, key=partial(sort_by_time, completed_lines)):
            args = (row, *completed_lines[row])
            yield CharacterCellLineEvent(*args)

        current_time += duration

    for row in sorted(pending_lines, key=partial(sort_by_time, pending_lines)):
        args = (row, *pending_lines[row])
        yield CharacterCellLineEvent(*args)


def default_themes():
    # type: ()-> Dict[str, str]
    """Return all the default color themes"""
    pattern = re.compile('base16-(?P<theme_name>.+).Xresources')
    themes = {}
    for file in pkg_resources.resource_listdir(__name__, XRESOURCES_DIR):
        match = pattern.fullmatch(file)
        if match:
            file_path = os.path.join(XRESOURCES_DIR, file)
            xresources_str = pkg_resources.resource_string(__name__, file_path).decode('utf-8')
            themes[match.group('theme_name')] = xresources_str
    return themes


def get_configuration(use_system_theme, theme_name, fileno):
    # type: (bool, str, int) -> (int, int, AsciiCastTheme)
    """Get configuration information related to terminal output rendering. If some information can
    not be gathered from the system, return the default configuration.
    """
    try:
        columns, lines = os.get_terminal_size(fileno)
    except OSError as e:
        lines = 24
        columns = 80
        logger.debug('Failed to get terminal size ({}), using default values '
                     'instead ({}x{})'.format(e, columns, lines))

    if use_system_theme:
        try:
            xresources_str = _get_xresources()
        except DisplayError:
            logger.debug('Failed to gather color information from the Xserver, '
                         'using fallback theme instead ("{}")'.format(theme_name))
            xresources_str = default_themes()[theme_name]
    else:
        xresources_str = default_themes()[theme_name]
    theme = _parse_xresources(xresources_str)

    return columns, lines, theme


def _get_xresources():
    # type: () -> str
    """Query the X server for the Xresources string of the default display"""
    d = display.Display()
    data = d.screen(0).root.get_full_property(Xatom.RESOURCE_MANAGER,
                                              Xatom.STRING)
    return data.value.decode('utf-8')


def _parse_xresources(xresources):
    # type: (str) -> AsciiCastTheme
    """Parse the Xresources string and return an AsciiCastTheme containing the color information

    The default text and background colors and the first 8 colors are required. If one of them is
    missing, KeyError is raised.
    """
    res_db = rdb.ResourceDB(string=xresources)

    colors = {}
    names = [('foreground', True), ('background', True)] + \
            [('color{}'.format(index), index < 8) for index in range(16)]
    for name, required in names:
        res_name = 'termtosvg.' + name
        res_class = res_name
        try:
            colors[name] = res_db[res_name, res_class]
        except KeyError:
            if required:
                raise

    palette = ':'.join(colors['color{}'.format(i)] for i in range(len(colors)-2))
    theme = AsciiCastTheme(fg=colors['foreground'],
                           bg=colors['background'],
                           palette=palette)
    return theme
