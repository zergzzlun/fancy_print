# fancy_print

Tiny non-blocking "typewriter" printing for Python — render text character by character without slowing your code.

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
```

### API Reference

```python
from fancy_print import fancy_print, fancy_print_flush, configure_fancy_print
```

- `fancy_print(*objects, end='\n', sep=' ', perform_logging=False, print_interval=0.015)`
  - Accepts any objects, joins them with `sep`, appends `end`, renders asynchronously with per-character delay, and optionally logs via `logging.info`.
- `fancy_print_flush(timeout=None)`
  - Blocks until the queue drains (or the optional timeout elapses), ensuring all prior output has been rendered.
- `configure_fancy_print(max_queue=None)`
  - Sets a maximum queue length (positive integer). When the queue would overflow, oldest messages are synchronously flushed before enqueuing the new one. Pass `None` to remove the cap.
