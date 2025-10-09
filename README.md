# fancy_print

<p align="left">
  <img src="https://raw.githubusercontent.com/zergzzlun/fancy_print/refs/heads/main/assets/logo.png" alt="fancy_print logo" height="256" />
  <img src="https://raw.githubusercontent.com/zergzzlun/fancy_print/refs/heads/main/assets/example_01.gif" alt="fancy_print exmpale" height="256" />
</p>

Tiny non-blocking "typewriter" and colorful printing for Python — render text character by character without slowing your code.

## Install

```
pip install -e .
```

## Usage

### Basic

```python
from fancy_print import fancy_print

fancy_print('Hello', 'world!', sep=', ', end='!\n')
fancy_print('Processing', perform_logging=True, print_interval=0.05)
fancy_print('Success', color='#ff0058')  # colour on TTYs
```

### API Reference

```python
from fancy_print import fancy_print, fancy_print_flush, configure_fancy_print
```

#### `fancy_print(*objects, end='\n', sep=' ', perform_logging=False, print_interval=0.015, color=None)`
- `*objects` (`Any`): values to render.
- `end` (`str`): terminator appended after the text.
- `sep` (`str`): inserted between each object.
- `perform_logging` (`bool`): emit the rendered text via `logging.info` when `True`.
- `print_interval` (`float`): per-character delay in seconds.
- `color` (`str | None`): named or hex colour applied on TTYs (e.g. `'red'`, `'#FF6600'`).

#### `fancy_print_flush(timeout=None)`
- `timeout` (`float | None`): seconds to wait for the queue to empty.

#### `configure_fancy_print(max_queue=None)`
- `max_queue` (`int | None`): positive integer cap for queued messages (`None` removes the cap).
