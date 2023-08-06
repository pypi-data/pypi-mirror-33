import sys
from unbuffered_input.runloop import Runloop


class InteractiveSearch(object):
    def __init__(self,
                 dataset=[],
                 max_visible_items=10,
                 initial_text='',
                 filter_func=lambda _: True,
                 item_to_string=lambda x: str(x)):
        self._dataset = dataset
        self._current_filtered_result = self._dataset
        assert 1 <= max_visible_items <= 100
        self._max_visible_items = max_visible_items
        self._highlighted_index = 0
        self._selected_index = -1
        self._current_keyword = initial_text
        self._filter_func = filter_func
        self._item_to_string = item_to_string

    def run(self):
        _scroll_up_window(self._max_visible_items + 1)
        _move_cursor_up(self._max_visible_items + 1)
        _save_cursor_position()
        self._filter()
        self._render()
        Runloop(
            should_exit=self._should_exit,
            on_change=self._on_change,
            on_enter=self._on_enter,
            on_down=self._on_down,
            on_up=self._on_up,
        ).start()
        for _ in range(self._max_visible_items):
            _move_cursor_down(1)
            _clear_current_line()
        _move_cursor_up(self._max_visible_items)
        _clear_current_line()
        if self._selected_index < 0 or self._selected_index >= len(self._dataset):
            return None
        return self._dataset[self._selected_index]

    def _should_exit(self):
        return self._selected_index >= 0

    def _on_change(self, s):
        self._current_keyword = s
        self._filter()
        self._render()

    def _on_enter(self, _):
        if self._highlighted_index < len(self._current_filtered_result):
            self._selected_index = self._highlighted_index

    def _on_down(self, _):
        if self._highlighted_index < len(self._current_filtered_result) - 1:
            self._highlighted_index += 1
            self._render()

    def _on_up(self, _):
        if self._highlighted_index > 0:
            self._highlighted_index -= 1
            self._render()

    def _filter(self):
        self._current_filtered_result = [item for item in self._dataset if self._filter_func(item)]

    def _render(self):
        _restore_cursor_position()
        _clear_current_line()
        _print_raw(self._current_keyword)
        _move_cursor_up(self._max_visible_items)
        index = 0
        if self._highlighted_index >= len(self._current_filtered_result):
            self._highlighted_index = 0
        for item in self._current_filtered_result[:self._max_visible_items]:
            _move_cursor_down(1)
            _clear_current_line()
            if index == self._highlighted_index:
                _start_underscore()
            _print_raw(self._item_to_string(item))
            _clear_format()
            index += 1
        for _ in range(index, self._max_visible_items):
            _move_cursor_down(1)
            _clear_current_line()
        _move_cursor_up(self._max_visible_items)
        _clear_current_line()
        _print_raw(self._current_keyword)


def _print_raw(text):
    sys.stdout.write('%s' % text)


def _clear_current_line():
    sys.stdout.write('\x1b[2K')
    _move_cursor_left(1000)


def _scroll_up_window(lines):
    sys.stdout.write('\x1bD' * lines)


def _move_cursor_up(lines):
    sys.stdout.write('\x1b[%dA' % lines)


def _move_cursor_down(lines):
    sys.stdout.write('\x1b[%dB' % lines)


def _move_cursor_left(columns):
    sys.stdout.write('\x1b[%dD' % columns)


def _save_cursor_position():
    sys.stdout.write('\x1b7')


def _restore_cursor_position():
    sys.stdout.write('\x1b8')


def _start_underscore():
    sys.stdout.write('\x1b[4m')


def _clear_format():
    sys.stdout.write('\x1b[0m')
