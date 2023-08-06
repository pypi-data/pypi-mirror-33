# Largely replaced by curses. Only used by scraper.

from sys import platform as sys_platform

if sys_platform == 'linux':
    class cl:
        purple = '\033[0;0;95m'
        cyan = '\033[0;0;96m'
        dcyan = '\033[0;0;36m'
        green = '\033[0;0;92m'
        yellow = '\033[0;0;93m'
        red = '\033[0;0;91m'
        bold = '\033[0;0;1m'
        underlined = '\033[0;0;4m'
        end = '\033[0;0;0m'

        white = '\033[1;37m'
        blue = '\033[0;34m'
        lblue = '\033[1;34m'
        lgreen = '\033[1;32m'
        lcyan = '\033[1;36;40m'
        lred = '\033[1;31m'
        lpurple = '\033[1;35m'
        orange = '\033[0;33;40m'
        brown = '\033[0;0;33m'
        grey = '\033[0;0;37m'
        lgrey = '\033[0;0;37m'

        # Format: _bg_fg
        _black_white = '\033[0;30;47m'

        _blue_yellow = '\033[1;33;44m'
        _blue_white = '\033[1;37;46m'
        _blue_red = '\033[1;34;41m'

        _cyan_white = '\033[1;37;46m'

        _green_white = '\033[1;37;42m'

        _red_black = '\033[7;31;40m'
        _red_blue = '\033[7;31;44m'
        _purple_white = '\033[1;37;45m'
        _purple_black = '\033[6;30;45m'
        _purple_purple = '\033[7;35;44m'
        _black_red = '\033[7;30;41m'
        _orange_black = '\033[0;30;43m'

        _flash_orange_black = '\033[5;30;43m'
else:
    import colorama

    colorama.init()


    class cl:
        purple = colorama.Fore.MAGENTA
        cyan = colorama.Fore.CYAN
        dcyan = colorama.Fore.CYAN
        green = colorama.Fore.CYAN
        yellow = colorama.Fore.YELLOW
        red = colorama.Fore.RED
        bold = colorama.Fore.WHITE
        underlined = colorama.Fore.WHITE

        end = colorama.Fore.RESET

        white = colorama.Fore.WHITE
        blue = colorama.Fore.BLUE
        lblue = colorama.Fore.BLUE
        lgreen = colorama.Fore.GREEN
        COLOR_CYAN = colorama.Fore.CYAN
        lcyan = colorama.Fore.CYAN
        lred = colorama.Fore.RED
        lpurple = colorama.Fore.MAGENTA
        brown = colorama.Fore.YELLOW
        grey = colorama.Fore.RESET
        lgrey = colorama.Fore.WHITE

        _red_black = colorama.Back.RED + colorama.Fore.BLACK
        _black_red = colorama.Back.BLACK + colorama.Fore.RED
        _orange_black = colorama.Back.YELLOW + colorama.Fore.BLACK

colour = {x: vars(cl)[x] for x in dir(cl) if
          not x.startswith('__')}  # Easier to write cl.COLOUR, but need dictionary functionality too.
cl_to_assign = [x for x in dir(cl) if not x.startswith('_')]

colours = [
    [cl.white, cl.end, cl.red, cl.purple],
    [cl.lcyan, cl.lblue, cl.brown, cl.blue],
]


def cl_seq_to_str(sequence):  # Translate an escape sequence to its corresponding colour/attribute
    for c in colour:
        if colour[c] == sequence:
            return c
        if c == sequence:
            return c
    raise Exception('Sequence:' + sequence + ' is not in colour dictionary')


def colour_alternating(*args):  # Translate a sequence of objects to a coloured string
    global colours
    tpl = []

    def aaa(*args):
        tpl_new = []
        for arg in args:
            if type(arg).__name__ in ['str', 'int', 'float', 'datetime.date']:
                tpl_new.append(str(arg))
            elif type(arg).__name__ in ['list', 'tuple']:
                for x in arg:
                    tpl_new += aaa([], x)
        return tpl_new

    tpl += aaa(args)
    to_print = ''
    for i in range(len(tpl)):
        try:
            to_print += colours[0][i % len(colours[0])] + tpl[i] + '  '
        except:
            print(tpl[i])
    colours[0], colours[1] = colours[1], colours[0]
    return to_print


def toprint_expanded(*args):
    to_print = ''
    for i in range(len(args)):
        try:
            to_print += args[i] + cl.end + '  '
        except TypeError:
            if int(float(args[i]))==float(int(args[i])):
                to_print += str(int(args[i])) + cl.end + '  '
            else:
                to_print += str(float(args[i])) + cl.end + '  '
    return to_print


def toprint_expanded_ls(*args):
    tpl = []

    def aaa(*args):
        tpl_new = []
        for arg in args:
            if type(arg).__name__ in ['str', 'int', 'float', 'datetime.date']:
                tpl_new.append(str(arg))
            elif type(arg).__name__ in ['list', 'tuple']:
                for x in arg:
                    tpl_new += aaa([], x)
        return tpl_new

    tpl += aaa(args)
    to_print = ''
    for i in range(len(tpl)):
        try:
            to_print += tpl[i] + cl.end + '  '
        except:
            pass
    return to_print
