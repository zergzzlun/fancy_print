# Zhaolun Zou 05/06/2024
import atexit
import sys
import time
import logging
from threading import Event, Thread
from dataclasses import dataclass
from queue import Queue, Empty
from typing import Optional

__all__ = ['fancy_print', 'fancy_print_flush']


@dataclass
class PrintMsg:
    text: str
    end: str
    perform_logging: bool
    print_interval: float


class FancyPrinter:
    def __init__(self) -> None:
        self._ingress: Queue = Queue()
        self._file = sys.stdout
        self._is_tty = hasattr(self._file, 'isatty') and self._file.isatty()
        self._worker: Optional[Thread] = None
        self._stop = Event()

    def enqueue(self, msg: PrintMsg) -> None:
        self._refresh_output_target()
        self._ensure_worker()
        self._ingress.put_nowait(msg)

    def flush(self, timeout: Optional[float] = None) -> None:
        if timeout is None:
            self._ingress.join()
            return
        deadline = time.perf_counter() + timeout
        while True:
            if self._ingress.unfinished_tasks == 0:
                return
            remaining = deadline - time.perf_counter()
            if remaining <= 0:
                return
            time.sleep(min(0.005, remaining))

    def _print_sync(self, msg: PrintMsg) -> None:
        if self._is_tty:
            self._print_tty(msg)
        else:
            self._print_line(msg)
        if msg.perform_logging:
            logging.info(msg.text)

    def _refresh_output_target(self) -> None:
        self._file = sys.stdout
        self._is_tty = hasattr(self._file, 'isatty') and self._file.isatty()

    def _ensure_worker(self) -> None:
        if self._worker and self._worker.is_alive():
            return
        self._stop.clear()
        self._worker = Thread(target=self._run, name='FancyPrinterWorker')
        self._worker.daemon = True
        self._worker.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                msg = self._ingress.get(timeout=0.1)
            except Empty:
                continue
            if msg is None:
                self._ingress.task_done()
                break
            try:
                self._print_sync(msg)
            finally:
                self._ingress.task_done()

    def stop(self) -> None:
        if self._worker and self._worker.is_alive():
            self._stop.set()
            self._ingress.put_nowait(None)
            self._worker.join(timeout=1)
        while True:
            try:
                msg = self._ingress.get_nowait()
            except Empty:
                break
            if msg is None:
                self._ingress.task_done()
                continue
            try:
                self._print_sync(msg)
            finally:
                self._ingress.task_done()
        self._worker = None
        self._stop.clear()

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
_SHUTDOWN_REGISTERED = False


def _get_printer() -> FancyPrinter:
    global _GLOBAL_FANCY_PRINTER, _SHUTDOWN_REGISTERED
    if _GLOBAL_FANCY_PRINTER is None:
        _GLOBAL_FANCY_PRINTER = FancyPrinter()
        if not _SHUTDOWN_REGISTERED:
            atexit.register(_shutdown_printer)
            _SHUTDOWN_REGISTERED = True
    return _GLOBAL_FANCY_PRINTER


def _shutdown_printer() -> None:
    if _GLOBAL_FANCY_PRINTER is None:
        return
    _GLOBAL_FANCY_PRINTER.stop()


def fancy_print(
    *objects: object,
    end: str = '\n',
    sep: str = ' ',
    perform_logging: bool = False,
    print_interval: float = 0.015,
) -> None:
    if not isinstance(end, str):
        raise TypeError(f'Parameter end should be str but got {type(end)}')
    if not isinstance(sep, str):
        raise TypeError(f'Parameter sep should be str but got {type(sep)}')
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

    text = sep.join(str(obj) for obj in objects) if objects else ''

    msg = PrintMsg(
        text=text,
        end=end,
        perform_logging=perform_logging,
        print_interval=print_interval,
    )

    printer = _get_printer()
    printer.enqueue(msg)


def fancy_print_flush(timeout: Optional[float] = None) -> None:
    printer = _GLOBAL_FANCY_PRINTER
    if printer is None:
        return
    printer.flush(timeout)


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
