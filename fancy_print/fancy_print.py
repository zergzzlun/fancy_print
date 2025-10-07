# Zhaolun Zou 05/06/2024
import sys
import time
import logging


def fancy_print(s, end='\n', perform_logging=False, print_interval=0.01):
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

    next_t = time.perf_counter()
    for char in s:
        print(char, end='')
        sys.stdout.flush()
        if print_interval > 0:
            next_t += print_interval
            remaining = next_t - time.perf_counter()
            if remaining > 0:
                time.sleep(remaining)

    print(end, end='')
    if perform_logging:
        logging.info(s)


def main():
    fancy_print('Testing......', end='')
    time.sleep(0.5)
    fancy_print(' Complete.')


if __name__ == '__main__':
    main()
