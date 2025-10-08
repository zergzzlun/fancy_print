import importlib
import io
import logging
import sys
import time
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for name in ['fancy_print.fancy_print', 'fancy_print']:
    if name in sys.modules:
        del sys.modules[name]

import pytest

fancy_print_module = importlib.import_module(
    'fancy_print.fancy_print'
)  # type: ignore

from fancy_print import (
    fancy_print,
    fancy_print_flush,
    configure_fancy_print,
)  # type: ignore  # noqa: E402


@pytest.fixture(autouse=True)
def reset_printer_state():
    printer = fancy_print_module._GLOBAL_FANCY_PRINTER
    if printer is not None:
        fancy_print_module.fancy_print_flush()
        printer.stop()
    fancy_print_module._GLOBAL_FANCY_PRINTER = None
    yield
    printer = fancy_print_module._GLOBAL_FANCY_PRINTER
    if printer is not None:
        fancy_print_module.fancy_print_flush()
        printer.stop()
    fancy_print_module._GLOBAL_FANCY_PRINTER = None


def test_fancy_print_writes_output(capsys, monkeypatch):
    buffer = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', buffer)
    fancy_print('hello', end='', print_interval=0)
    fancy_print_module.fancy_print_flush()
    assert buffer.getvalue() == 'hello'


def test_fancy_print_logs_when_requested(caplog, monkeypatch):
    buffer = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', buffer)
    with caplog.at_level(logging.INFO):
        fancy_print('log me', perform_logging=True, print_interval=0)
        fancy_print_module.fancy_print_flush()
    assert 'log me' in caplog.text


def test_fancy_print_handles_arbitrary_objects(monkeypatch):
    buffer = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', buffer)
    fancy_print('value:', 123, {'a': 1}, sep='|', end='', print_interval=0)
    fancy_print_module.fancy_print_flush()
    assert buffer.getvalue() == "value:|123|{'a': 1}"


def test_fancy_print_rejects_non_bool_logging():
    with pytest.raises(TypeError):
        fancy_print('hello', perform_logging='yes')  # type: ignore[arg-type]


def test_fancy_print_rejects_non_str_end():
    with pytest.raises(TypeError):
        fancy_print('hello', end=123)  # type: ignore[arg-type]


def test_fancy_print_rejects_non_str_sep():
    with pytest.raises(TypeError):
        fancy_print('hello', sep=123)  # type: ignore[arg-type]


def test_fancy_print_rejects_non_numeric_interval():
    with pytest.raises(TypeError):
        fancy_print('hello', print_interval='fast')  # type: ignore[arg-type]


def test_fancy_print_rejects_negative_interval():
    with pytest.raises(ValueError):
        fancy_print('hello', print_interval=-0.1)


def test_fancy_print_non_blocking(monkeypatch):
    class FakeTTY(io.StringIO):
        def isatty(self) -> bool:
            return True

    buffer = FakeTTY()
    monkeypatch.setattr(sys, 'stdout', buffer)
    start = time.perf_counter()
    fancy_print('slowwwwwwwwwww', end='', print_interval=0.02)
    duration = time.perf_counter() - start
    assert duration < 0.01


def test_configure_max_queue_flushes_oldest(monkeypatch):
    class FakeTTY(io.StringIO):
        def isatty(self) -> bool:
            return True

    buffer = FakeTTY()
    monkeypatch.setattr(sys, 'stdout', buffer)

    orig_print_tty = fancy_print_module.FancyPrinter._print_tty
    start_event = threading.Event()
    release_event = threading.Event()

    def controlled_print_tty(self, msg):
        if msg.text == 'slow':
            start_event.set()
            release_event.wait()
        orig_print_tty(self, msg)

    monkeypatch.setattr(
        fancy_print_module.FancyPrinter,
        '_print_tty',
        controlled_print_tty,
        raising=False,
    )

    configure_fancy_print(max_queue=1)

    fancy_print('slow', end='', print_interval=0.01)
    assert start_event.wait(0.5)

    fancy_print('second', end='', print_interval=0)
    fancy_print('third', end='', print_interval=0)

    assert 'second' in buffer.getvalue()
    assert 'third' not in buffer.getvalue()

    release_event.set()
    fancy_print_flush()

    final = buffer.getvalue()
    assert 'third' in final
    assert final.index('second') < final.index('third')


def test_configure_max_queue_rejects_non_positive():
    with pytest.raises(ValueError):
        configure_fancy_print(max_queue=0)


def test_fancy_print_hex_color_on_tty(monkeypatch):
    class FakeTTY(io.StringIO):
        def isatty(self) -> bool:
            return True

    buffer = FakeTTY()
    monkeypatch.setattr(sys, 'stdout', buffer)
    fancy_print('colorful', color='#00ff00', print_interval=0)
    fancy_print_module.fancy_print_flush()
    output = buffer.getvalue()
    assert '\033[38;2;0;255;0m' in output
    assert output.endswith('\033[0m\n')


def test_fancy_print_color_skipped_for_non_tty(monkeypatch):
    buffer = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', buffer)
    fancy_print('plain', color='red', print_interval=0)
    fancy_print_module.fancy_print_flush()
    assert '\033' not in buffer.getvalue()


def test_fancy_print_rejects_bad_color():
    with pytest.raises(ValueError):
        fancy_print('oops', color='not-a-color')
