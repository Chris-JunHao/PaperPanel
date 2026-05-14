# AGENTS.md

Guidance for coding agents working in this repository.

## Project

PaperPanel is a lightweight Python tool for composing academic screenshot panels.
It uses Python and Pillow to combine already preprocessed PNG screenshots into
2-panel or 3-panel horizontal figures.

## Rules

- Use Python and Pillow only unless the user explicitly approves more
  dependencies.
- Do not crop, blur, sharpen, denoise, color-correct, or otherwise enhance image
  contents.
- Treat input images as already preprocessed PNG files.
- Read input images from `input/`.
- Save generated figures to `output/`.
- Read the group definition file from `input/groups.txt`.
- Support 2-panel and 3-panel horizontal layouts.
- Add labels such as `(a)`, `(b)`, and `(c)` under each subfigure.
- Save output images as PNG files with 300 dpi metadata.
- Keep the code simple, readable, and suitable for a small GitHub project.
- After code changes, run a minimal local test.
- Before finishing, summarize changed files and how to run the tool.

## Implementation Preferences

- Prefer small functions with clear names over broad abstractions.
- Keep command-line behavior predictable and easy to document.
- Validate user input and report clear errors for missing files, invalid groups,
  unsupported panel counts, or non-PNG inputs.
- Avoid modifying image contents beyond layout composition, spacing, labels, and
  final PNG output metadata.
- Keep tests focused on layout behavior, path handling, validation, and output
  creation.

