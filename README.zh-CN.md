语言： [English](README.md) | [中文](README.zh-CN.md)
# PaperPanel

PaperPanel 是一个轻量级的 Python + Pillow 工具，用于把已经预处理好的
学术截图 PNG 拼接成 2 栏或 3 栏的论文插图。

它不会裁剪、模糊、锐化、降噪、增强或修改图片内容。它只会根据排版需要
缩放图片、放置到白色画布上、添加子图标签，并以 300 dpi 元数据保存为
PNG 文件。

## 安装与运行

建议先创建 Python 虚拟环境，再安装依赖并运行工具。

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python compose_figures.py
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python compose_figures.py
```

真实论文或毕业论文截图应只放在本地的 `input/` 目录中。项目已通过
`.gitignore` 忽略这些图片，避免误提交隐私文件或大文件。`output/` 中生成的
拼图结果也会被忽略，因为它们可以随时重新生成。

## 输入文件

把源 PNG 截图放入 `input/` 目录。

在 `input/groups.txt` 中定义需要生成的图片组。每一行非空、非注释内容表示
一个输出图，格式如下：

```text
output_file | layout | image1 | label1 | image2 | label2 | image3 | label3
```

`layout` 支持以下选项：

- `h2`：横向 2 图布局
- `h3`：横向 3 图布局
- `v2`：纵向 2 图布局
- `v3`：纵向 3 图布局

为了兼容旧配置，也支持数字写法：

- `2` 等同于 `h2`
- `3` 等同于 `h3`

旧格式横向 2 图示例：

```text
my_figure.png | 2 | panel_a.png | (a) | panel_b.png | (b)
```

推荐写法的横向 2 图示例：

```text
my_horizontal_2.png | h2 | panel_a.png | (a) | panel_b.png | (b)
```

横向 3 图示例：

```text
my_horizontal_3.png | h3 | panel_a.png | (a) | panel_b.png | (b) | panel_c.png | (c)
```

纵向 2 图示例：

```text
my_vertical_2.png | v2 | panel_a.png | (a) | panel_b.png | (b)
```

纵向 3 图示例：

```text
my_vertical_3.png | v3 | panel_a.png | (a) | panel_b.png | (b) | panel_c.png | (c)
```

图片路径相对于 `input/`。输出文件会保存到 `output/`。

横向布局会把所有图片缩放到相同的 `TARGET_HEIGHT`，然后从左到右排列。纵向
布局会把所有图片缩放到相同的 `TARGET_WIDTH`，然后从上到下排列。每张子图的
标签会居中放在图片下方。

## 配置示例

`input/groups.txt` 可以写成：

```text
# PaperPanel example configuration
example_old_2panel.png | 2 | example_a.png | (a) | example_b.png | (b)
example_h2.png | h2 | example_a.png | (a) | example_b.png | (b)
example_h3.png | h3 | example_a.png | (a) | example_b.png | (b) | example_c.png | (c)
example_v2.png | v2 | example_a.png | (a) | example_b.png | (b)
example_v3.png | v3 | example_a.png | (a) | example_b.png | (b) | example_c.png | (c)
```

空行和以 `#` 开头的行会被忽略。如果某一组配置格式错误，或者引用了不存在的
图片，程序会打印清晰的警告并继续处理后续配置。

## 可调参数

主要排版参数位于 `compose_figures.py` 顶部：

```python
TARGET_HEIGHT = 900
TARGET_WIDTH = 1200
PADDING = 40
GAP = 30
LABEL_SIZE = 36
LABEL_GAP = 10
```

通常只需要调整这些常量即可改变输出图的整体尺寸、边距、图片间距和标签大小。

