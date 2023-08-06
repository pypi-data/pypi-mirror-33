import os
import shlex
import struct
import logging
import platform
import subprocess
import termcolor



logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

_color_policy = True
_output_policy = True
_debug_policy = False
_debug = False
_message = ''


def _get_width():
    result = get_terminal_size()
    return result[0]


def debug_on():
    global _debug
    _debug = True


def debug_off():
    global _debug
    _debug = False


def output_control(func):
    def wrapper(*args, **kwargs):
        global _output_policy
        if _output_policy:
            func(*args, **kwargs)
    return wrapper


def debug_control(func):
    def wrapper(*args, **kwargs):
        global _debug_policy, _debug
        if not _debug or (_debug and _debug_policy):
            func(*args, **kwargs)
    return wrapper


def set_color_policy(color_policy):
    global _color_policy
    _color_policy = color_policy


def set_output_policy(output_policy):
    global _output_policy
    _output_policy = output_policy


def set_debug_policy(debug):
    global _debug_policy
    _debug_policy = debug


@output_control
def color(full_text):
    results = full_text.split('[')
    for result in results:
        if result and result != '':
            second_results = result.split(']')
            color, text = second_results[0], second_results[1]
            _print_colored(text, color, end='')


@output_control
def title_1(name=None):
    if name:
        _step(name, 'white', '=', '[', ']')
    else:
        _step('', 'white', '=')


@output_control
def title_2(name=None):
    if name:
        _step(name, 'white', '-', '[', ']')
    else:
        _step('', 'white', '-')


@output_control
def title_3(name=None):
    if name:
        _step(name, 'yellow', '-')
    else:
        _step('', 'yellow', '-')


@output_control
def title_4(name=None):
    if name:
        _step(name, 'magenta', '-')
    else:
        _step('', 'green', '-')


@output_control
def start_step(name):
    _step(name, 'yellow', '-')


@output_control
def error_step(name):
    _step(name, 'red', '-')


@output_control
def category(message):
    _print_colored('[' + message + ']', 'magenta')


def error(message):
    _print_colored(message, 'red')


@output_control
def warning(message):
    _print_colored(message, 'orange')


@output_control
def info(message):
    _print_colored(message, 'cyan')


def _step(name, text_color, character, before='', after=''):
    width = _get_width()
    if name != '':
        name = ' {} '.format(name)
    text = '{}{}{}'.format(before, name, after)
    _print_colored(text.center(width, character), text_color)


@output_control
def push(message):
    pass


@output_control
def infos(infos, attrs):
    text = ''
    spaces = {}
    shift = 2

    for info in infos:
        for attr in attrs:
            name = attr[0]
            info_name_len = len(str(info[name]))
            if name in spaces:
                if info_name_len + shift > spaces[name]:
                    spaces[name] = info_name_len + shift
            else:
                spaces[name] = info_name_len + shift

    for info in infos:
        for attr in attrs:
            name = attr[0]
            color = attr[1]
            text = ''
            if len(attr) > 2:
                text = attr[2]

            if isinstance(info[name], tuple):
                info_name = str(info[name][0])
                info_name_len = len(info_name)
                full_text = text + info_name
                color = info[name][1]
            else:
                info_name = str(info[name])
                info_name_len = len(info_name)
                full_text = text + info_name

            _print_colored(full_text, color, end='')
            _print_colored(' ' * (spaces[name] - info_name_len), end='')
        _print_colored()


@output_control
def clear():
    pass


def colored(*args, **kwargs):
    _print_colored(*args, **kwargs)

@output_control
@debug_control
def _print_colored(text='', color=None, highlight=None, end='\n'):
    global _message
    global _color_policy

    if _color_policy:

        if highlight and color:
            _message += termcolor.colored(text, color, highlight)
        elif color:
            _message += termcolor.colored(text, color)
        else:
            _message += termcolor.colored(text)
    else:
        _message += text

    if end == '\n':
        logger.info(_message)
        _message = ''


def get_terminal_size():
    """ getTerminalSize()
     - get width and height of console
     - works on linux,os x,windows,cygwin(windows)
     originally retrieved from:
     http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        print('default')
        tuple_xy = (80, 25)      # default value
    return tuple_xy


def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        pass


def _get_terminal_size_tput():
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except:
        pass


def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])