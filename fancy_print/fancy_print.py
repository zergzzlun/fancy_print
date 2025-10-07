# Zhaolun Zou 05/06/2024
import sys
import time
import logging


def fancy_print(s, end='\n', log=False, print_interval=0.01):
    if not isinstance(s, str):
        raise TypeError(f'Content should be str but got {type(s)}')
    if not isinstance(log, bool):
        raise TypeError(f'Parameter log should be boolean: {log}')
    for char in s:
        print(char, end='')
        sys.stdout.flush()
        time.sleep(print_interval)
    print(end, end='')
    if log:
        logging.info(s)


def main():
    fancy_print('Testing......', end='')
    time.sleep(0.5)
    fancy_print(' Complete.')


if __name__ == '__main__':
    main()
