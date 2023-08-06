import sys
from unbuffered_input.runloop import Runloop


def on_up(_):
    print_raw('up')


def on_down(_):
    print_raw('down')


def on_left(_):
    print_raw('left')


def on_right(_):
    print_raw('right')


def on_change(s):
    print_raw(s)


def on_enter(s):
    print_raw(s)


def print_raw(s):
    sys.stdout.write('%s\x1b[1000D\n' % s)


def run():
    Runloop(
        on_up=on_up,
        on_down=on_down,
        on_left=on_left,
        on_right=on_right,
        on_change=on_change,
        on_enter=on_enter
    ).start()
