import importlib
import io
import logging
import sys
import time
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

from fancy_print import fancy_print  # type: ignore  # noqa: E402


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
