# imgstat

A small command-line tool that reports statistics about an image and prints an
ASCII intensity histogram right in your terminal. No GUI, no heavy dependencies
— just a clean, testable utility.

## Features

- Per-channel `min`, `max`, `mean`, and `std` for grayscale, RGB, RGBA, and CMYK images
- A horizontal ASCII histogram of pixel intensities
- Machine-readable `--json` output for scripting
- Handles multiple files in one invocation
- A small library core (`imgstat.core`) you can import and reuse

## Installation

```bash
git clone https://github.com/<your-username>/imgstat.git
cd imgstat
pip install -e .
```

Requires Python 3.9+.

## Usage

```bash
imgstat path/to/image.png
```

Example output:

```
path/to/image.png
  size    : 64 x 48 px
  mode    : RGB
  channels: 3

  channel       min      max      mean       std
  -------- -------- -------- --------- ---------
  red           0.0    255.0    127.03     74.69
  green         0.0    255.0    127.03     74.69
  blue        120.0    120.0    120.00      0.00

  intensity histogram:

      0.0 | ██████
    106.2 | ████████████████████████████████████████
    127.5 | █████
    233.8 | ██████
```

### Options

| Flag        | Description                                  |
| ----------- | -------------------------------------------- |
| `--json`    | Emit machine-readable JSON instead of text   |
| `--bins N`  | Histogram bucket count (default: 32)         |
| `--no-hist` | Skip the histogram in text output            |
| `--version` | Print the version and exit                   |

### As a library

```python
from imgstat.core import load_image, compute_stats

arr, mode = load_image("image.png")
stats = compute_stats(arr, mode)
print(stats.channels[0].mean)
```

## Development

```bash
pip install -e ".[dev]"
pytest
```
