import io
import logging
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for name in ['fancy_print.fancy_print', 'fancy_print']:
    if name in sys.modules:
        del sys.modules[name]

from fancy_print import fancy_print  # type: ignore  # noqa: E402


def test_fancy_print_writes_output(capsys, monkeypatch):
    buffer = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', buffer)
    fancy_print('hello', end='', print_interval=0)
    assert buffer.getvalue() == 'hello'


def test_fancy_print_logs_when_requested(caplog, monkeypatch):
    buffer = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', buffer)
    with caplog.at_level(logging.INFO):
        fancy_print('log me', perform_logging=True, print_interval=0)
    assert 'log me' in caplog.text


def test_fancy_print_rejects_non_strings():
    with pytest.raises(TypeError):
        fancy_print(123)  # type: ignore[arg-type]


def test_fancy_print_rejects_non_bool_logging():
    with pytest.raises(TypeError):
        fancy_print('hello', perform_logging='yes')  # type: ignore[arg-type]


def test_fancy_print_rejects_non_numeric_interval():
    with pytest.raises(TypeError):
        fancy_print('hello', print_interval='fast')  # type: ignore[arg-type]


def test_fancy_print_rejects_negative_interval():
    with pytest.raises(ValueError):
        fancy_print('hello', print_interval=-0.1)
