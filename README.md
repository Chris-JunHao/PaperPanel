# PaperPanel

PaperPanel is a lightweight Python + Pillow tool for composing already
preprocessed academic PNG screenshots into 2-panel or 3-panel horizontal
figures.

It does not crop, blur, sharpen, denoise, or enhance image contents. It only
resizes panels to a shared height, places them on a white canvas, adds labels,
and saves PNG output with 300 dpi metadata.

## Setup

Create and activate a Python virtual environment before installing
dependencies.

Windows PowerShell:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python compose_figures.py
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python compose_figures.py
```

Real thesis screenshots should be placed in `input/` for local use only. They
are ignored by Git to avoid accidentally committing private or large image
files. Generated figures in `output/` are also ignored because they can be
regenerated.

## Input

Put source PNG screenshots in `input/`.

Define figure groups in `input/groups.txt`. Each non-empty, non-comment line has
this format:

```text
output_file | cols | image1 | label1 | image2 | label2 | image3 | label3
```

`cols` must be `2` or `3`.

For a 2-panel figure:

```text
my_figure.png | 2 | panel_a.png | (a) | panel_b.png | (b)
```

For a 3-panel figure:

```text
my_figure.png | 3 | panel_a.png | (a) | panel_b.png | (b) | panel_c.png | (c)
```

Image paths are relative to `input/`. Output files are saved under `output/`.

## Usage

```bash
python compose_figures.py
```

The script creates `output/` automatically and continues processing other groups
if one line has missing files or invalid formatting.

## Editable Layout Constants

The main layout constants are at the top of `compose_figures.py`:

```python
TARGET_HEIGHT = 900
PADDING = 40
GAP = 30
LABEL_SIZE = 36
LABEL_GAP = 10
```
