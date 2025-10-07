# Zhaolun Zou 05/06/2024
import sys
import time
import logging
from dataclasses import dataclass
from queue import SimpleQueue, Empty
from typing import Optional

__all__ = ['fancy_print']


@dataclass
class PrintMsg:
    text: str
    end: str
    perform_logging: bool
    print_interval: float


class FancyPrinter:
    def __init__(self) -> None:
        self._ingress: SimpleQueue = SimpleQueue()
        self._file = sys.stdout
        self._is_tty = hasattr(self._file, 'isatty') and self._file.isatty()

    def enqueue(self, msg: PrintMsg) -> None:
        self._ingress.put_nowait(msg)

    def process_all_sync(self) -> None:
        '''Drain all queued messages synchronously (no worker yet).'''
        while True:
            try:
                msg = self._ingress.get_nowait()
            except Empty:
                break
            self._print_sync(msg)

    def _print_sync(self, msg: PrintMsg) -> None:
        if self._is_tty:
            self._print_tty(msg)
        else:
            self._print_line(msg)
        if msg.perform_logging:
            logging.info(msg.text)

    def _print_line(self, msg: PrintMsg) -> None:
        self._file.write(msg.text)
        self._file.write(msg.end)
        self._file.flush()

    def _print_tty(self, msg: PrintMsg) -> None:
        next_t = time.perf_counter()
        for ch in msg.text:
            self._file.write(ch)
            self._file.flush()
            if msg.print_interval > 0:
                next_t += msg.print_interval
                remain = next_t - time.perf_counter()
                if remain > 0:
                    time.sleep(remain)
        self._file.write(msg.end)
        self._file.flush()


_GLOBAL_FANCY_PRINTER: Optional[FancyPrinter] = None


def _get_printer() -> FancyPrinter:
    global _GLOBAL_FANCY_PRINTER
    if _GLOBAL_FANCY_PRINTER is None:
        _GLOBAL_FANCY_PRINTER = FancyPrinter()
    return _GLOBAL_FANCY_PRINTER


def fancy_print(
    s: str,
    end: str = '\n',
    perform_logging: bool = False,
    print_interval: float = 0.015,
) -> None:
    if not isinstance(s, str):
        raise TypeError(f'Content should be str but got {type(s)}')
    if not isinstance(perform_logging, bool):
        raise TypeError(
            f'Parameter perform_logging should be boolean: {perform_logging}'
        )
    if not isinstance(print_interval, (int, float)):
        raise TypeError(
            f'Parameter print_interval must be numeric: {print_interval}'
        )
    if print_interval < 0:
        raise ValueError(
            f'Parameter print_interval must be non-negative: {print_interval}'
        )

    msg = PrintMsg(
        text=s,
        end=end,
        perform_logging=perform_logging,
        print_interval=print_interval,
    )

    printer = _get_printer()
    printer.enqueue(msg)
    printer.process_all_sync()


def main():
    def test_fancy_print(test_code: str) -> None:
        fancy_print(f'Testing {test_code}......', end='')
        time.sleep(0.5)
        fancy_print(' Complete.')
    test_fancy_print('A')
    test_fancy_print('B')
    test_fancy_print('C')


if __name__ == '__main__':
    main()
