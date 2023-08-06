import string


class Runloop(object):
    def __init__(self,
                 on_change=None,
                 on_enter=None,
                 on_up=None,
                 on_down=None,
                 on_left=None,
                 on_right=None,
                 should_exit=None):
        self._on_change = on_change
        self._on_up = on_up
        self._on_down = on_down
        self._on_left = on_left
        self._on_right = on_right
        self._on_enter = on_enter
        self._should_exit = should_exit
        self._characters_so_far = []

    def start(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        escape_sequences_to_callbacks = {
            'A': self._on_up,
            'B': self._on_down,
            'C': self._on_right,
            'D': self._on_left,
        }
        try:
            tty.setraw(sys.stdin.fileno())
            while not self._should_exit or not self._should_exit():
                ch = sys.stdin.read(1)
                ch_value = ord(ch)
                if ch_value == 3:
                    # Ctrl + C
                    break

                if ch_value == 27:
                    # Escape
                    next_ch = sys.stdin.read(1)
                    if next_ch == '[':
                        escape_sequence = sys.stdin.read(1)
                        self._trigger_callback(escape_sequences_to_callbacks.get(escape_sequence))
                    continue
                if ch_value == 13:
                    self._trigger_callback(self._on_enter)
                    continue
                if ch_value == 127:
                    if self._characters_so_far:
                        self._characters_so_far.pop()
                        self._trigger_callback(self._on_change)
                    continue
                # TODO handle utf-8 sequences
                if ch in string.printable:
                    self._characters_so_far.append(ch)
                    self._trigger_callback(self._on_change)
                    continue
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _trigger_callback(self, callback_func):
        if callback_func:
            callback_func(''.join(self._characters_so_far))
