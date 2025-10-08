# fancy_print

Tiny utility that prints strings one character at a time.

## Install

```
pip install -e .
```

## Usage

```python
from fancy_print import fancy_print

# behaves like print()
fancy_print('Hello', 'world!', sep=', ', end='!\n')

# log output and slow down rendering
fancy_print('Processing', perform_logging=True, print_interval=0.05)
```

Parameters:
- `sep`: separator inserted between arguments (default `' '`).
- `end`: terminator appended after the text (default `'\n'`).
- `perform_logging`: when `True`, also emits the final text through `logging.info`.
- `print_interval`: delay in seconds between characters (default `0.015`).
