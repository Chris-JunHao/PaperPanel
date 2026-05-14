from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont


TARGET_HEIGHT = 900
TARGET_WIDTH = 1200
PADDING = 40
GAP = 30
LABEL_SIZE = 36
LABEL_GAP = 10

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
GROUPS_FILE = INPUT_DIR / "groups.txt"


def warn(line_number, message):
    print(f"Warning: line {line_number}: {message}")


def load_font(size):
    """Load a common system font across Windows, macOS, and Linux."""
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]

    for path in candidates:
        try:
            if Path(path).exists():
                return ImageFont.truetype(path, size)
        except OSError:
            pass

    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def parse_layout(value, line_number):
    normalized = value.lower()
    old_layouts = {"2": ("h", 2), "3": ("h", 3)}
    new_layouts = {
        "h2": ("h", 2),
        "h3": ("h", 3),
        "v2": ("v", 2),
        "v3": ("v", 3),
    }

    if normalized in old_layouts:
        return old_layouts[normalized]
    if normalized in new_layouts:
        return new_layouts[normalized]

    warn(line_number, f"layout must be 2, 3, h2, h3, v2, or v3, got {value!r}")
    return None


def parse_group(line, line_number):
    parts = [part.strip() for part in line.split("|")]
    if len(parts) < 2:
        warn(line_number, "expected: output_file | layout | image1 | label1 | ...")
        return None

    output_file = parts[0]
    if not output_file:
        warn(line_number, "missing output file name")
        return None

    layout = parse_layout(parts[1], line_number)
    if layout is None:
        return None
    direction, panel_count = layout

    expected_parts = 2 + panel_count * 2
    if len(parts) != expected_parts:
        warn(
            line_number,
            f"expected {expected_parts} fields for layout={parts[1]}, got {len(parts)}",
        )
        return None

    pairs = []
    for index in range(panel_count):
        image_name = parts[2 + index * 2]
        label = parts[3 + index * 2]
        if not image_name or not label:
            warn(line_number, "image paths and labels cannot be empty")
            return None
        if Path(image_name).is_absolute():
            warn(line_number, f"image path must be relative to input/: {image_name}")
            return None
        if Path(image_name).suffix.lower() != ".png":
            warn(line_number, f"input image must be a PNG: {image_name}")
            return None
        pairs.append((image_name, label))

    output_path = Path(output_file)
    if output_path.is_absolute():
        warn(line_number, f"output file must be relative to output/: {output_file}")
        return None
    if output_path.suffix.lower() != ".png":
        warn(line_number, f"output file must be a PNG: {output_file}")
        return None

    return output_path, direction, pairs


def load_and_resize(image_name, line_number, direction):
    path = INPUT_DIR / image_name
    if not path.exists():
        warn(line_number, f"missing input image: {path}")
        return None

    try:
        image = Image.open(path).convert("RGB")
    except OSError as exc:
        warn(line_number, f"could not open {path}: {exc}")
        return None

    width, height = image.size
    if width <= 0 or height <= 0:
        warn(line_number, f"invalid image dimensions: {path}")
        return None

    if direction == "h":
        target_width = round(width * TARGET_HEIGHT / height)
        size = (target_width, TARGET_HEIGHT)
    else:
        target_height = round(height * TARGET_WIDTH / width)
        size = (TARGET_WIDTH, target_height)

    return image.resize(size, Image.Resampling.LANCZOS)


def compose_horizontal(output_path, images, labels, label_sizes, font):
    label_height = max(height for _, height in label_sizes)
    content_width = sum(image.width for image in images) + GAP * (len(images) - 1)
    canvas_width = content_width + PADDING * 2
    canvas_height = TARGET_HEIGHT + LABEL_GAP + label_height + PADDING * 2
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)

    x = PADDING
    image_y = PADDING
    label_y = PADDING + TARGET_HEIGHT + LABEL_GAP

    for image, label, (label_width, _) in zip(images, labels, label_sizes):
        canvas.paste(image, (x, image_y))
        label_x = x + (image.width - label_width) / 2
        draw.text((label_x, label_y), label, fill="black", font=font)
        x += image.width + GAP

    return save_canvas(canvas, output_path)


def compose_vertical(output_path, images, labels, label_sizes, font):
    label_height = max(height for _, height in label_sizes)
    panel_heights = [image.height + LABEL_GAP + label_height for image in images]
    content_height = sum(panel_heights) + GAP * (len(images) - 1)
    canvas_width = TARGET_WIDTH + PADDING * 2
    canvas_height = content_height + PADDING * 2
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)

    y = PADDING

    for image, label, (label_width, _) in zip(images, labels, label_sizes):
        image_x = PADDING + (TARGET_WIDTH - image.width) / 2
        canvas.paste(image, (round(image_x), y))
        label_x = PADDING + (TARGET_WIDTH - label_width) / 2
        label_y = y + image.height + LABEL_GAP
        draw.text((label_x, label_y), label, fill="black", font=font)
        y += image.height + LABEL_GAP + label_height + GAP

    return save_canvas(canvas, output_path)


def save_canvas(canvas, output_path):
    OUTPUT_DIR.mkdir(exist_ok=True)
    final_path = OUTPUT_DIR / output_path
    final_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(final_path, "PNG", dpi=(300, 300))
    return final_path


def compose_group(output_path, direction, pairs, line_number, font):
    images = []
    labels = []

    for image_name, label in pairs:
        image = load_and_resize(image_name, line_number, direction)
        if image is None:
            return None
        images.append(image)
        labels.append(label)

    measure = Image.new("RGB", (1, 1), "white")
    draw = ImageDraw.Draw(measure)
    label_sizes = [text_size(draw, label, font) for label in labels]

    if direction == "h":
        return compose_horizontal(output_path, images, labels, label_sizes, font)
    return compose_vertical(output_path, images, labels, label_sizes, font)


def process_groups():
    if not GROUPS_FILE.exists():
        print(f"Error: missing group definition file: {GROUPS_FILE}")
        return 1

    font = load_font(LABEL_SIZE)
    outputs = []

    with GROUPS_FILE.open("r", encoding="utf-8") as groups:
        for line_number, raw_line in enumerate(groups, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            group = parse_group(line, line_number)
            if group is None:
                continue

            output_path, direction, pairs = group
            final_path = compose_group(output_path, direction, pairs, line_number, font)
            if final_path is not None:
                outputs.append(final_path)
                print(f"Created: {final_path}")

    if not outputs:
        print("No figures were created.")

    return 0


if __name__ == "__main__":
    sys.exit(process_groups())
