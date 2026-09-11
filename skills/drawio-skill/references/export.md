# 导出模式、命令与降级策略

在涉及输出图片、PDF、SVG 交付物或排查 Draw.io CLI 行为时查阅本文档。

## 导出模式选型决策

| 模式 | 适用场景 | 内嵌二次编辑数据 | 字体表现行为 |
|---|---|---:|---|
| **预览 PNG（Preview PNG）** | 视觉自检与用户快速审阅 | 否 | 栅格位图化 |
| **可编辑格式（Editable PNG/SVG/PDF）** | 用户需要在 Draw.io 中重新打开并编辑 | 是（带 `-e` 参数） | SVG 依赖渲染宿主环境 |
| **Office 安全格式（PPT/Office-safe SVG）** | PowerPoint、Office 嵌入、严苛跨机器字体排版 | 否（单独交付 `.drawio`） | 字体轮廓化转换为绝对矢量路径 |

切勿承诺单个 SVG 文件既能无损二次直接编辑，又能在各类不同机器上的 Office 中保证绝对零排版错乱。当两者均需要时，将 `.drawio` 源码与 PPT 安全矢量图一同交付。

## 外部运行依赖

通过 `draw.io`、`drawio`、macOS 应用程序绝对路径或 Windows 安装路径定位客户端。在 Linux 无头（Headless）环境中，使用 `xvfb-run` 并追加 `--disable-gpu`；若以 root 用户身份运行，在命令末尾追加 `--no-sandbox`。

生成 PPT 安全 SVG 额外需要系统中已安装 Poppler 的 `pdftocairo`，且导出宿主机器已安装所需字体。

## 预览 PNG 导出

**切勿携带 `-e` 参数：**

```bash
draw.io -x -f png -s 2 -b 10 -o diagram.png input.drawio
```

Linux 无头环境执行：

```bash
xvfb-run -a --server-args="-screen 0 1920x1080x24" \
  draw.io -x -f png -s 2 -b 10 -o diagram.png input.drawio --disable-gpu
```

质检预览图必须保持不透明底色，以防黑色文本在自动将透明通道叠加黑底的视觉模型中被误判为丢失。若需核实透明效果本身，另行导出一份带 `-t` 的测试图。

## 最终可编辑格式导出

```bash
draw.io -x -f png -e -t -s 2 -b 10 -o diagram.drawio.png input.drawio
python3 <this-skill-dir>/scripts/repair_png.py diagram.drawio.png

draw.io -x -f svg -e -b 10 -o diagram.drawio.svg input.drawio
draw.io -x -f pdf -e -b 10 -o diagram.drawio.pdf input.drawio
```

统一采用双扩展名（如 `.drawio.png`）以明确标识包含内嵌 XML 数据。针对每个导出的带 `-e` 的 PNG，必须运行 `repair_png.py` 修复 CLI 已知的文件末尾 IEND 块截断缺陷。

## PowerPoint / Office 安全矢量 SVG

```bash
python3 <this-skill-dir>/scripts/export_ppt_svg.py input.drawio diagram.svg
```

该确定性流水线会自动完成：调用 Draw.io 渲染裁剪后的 PDF、将 PDF 文字字形直接转为 SVG 矢量闭合路径、移除 PDF 默认附加的纯白底面、生成以 `<svg` 开头的纯净文件。

运行前确认机器已安装所需字体。在 Linux 下可使用：

```bash
fc-match 'Noto Sans CJK SC'
```

## 结构与格式终检命令

```bash
python3 <this-skill-dir>/scripts/validate_drawio.py input.drawio
xmllint --noout output.svg
file --mime-type output.svg
```

针对 PPT 安全 SVG，还必须断言文件中绝无遗留的 `<text>` 或 `<foreignObject>` 标签：

```bash
rg -n '<text|foreignObject' output.svg
```

预期输出应为空。

## CLI 异常处理梯度

遇到报错时按以下顺序排查解决：

1. 通过 `draw.io --version` 或 `drawio --version` 验证程序是否真实就绪；
2. 在 Linux 上，包裹前缀 `xvfb-run -a`；
3. 追加 `--disable-gpu` 参数；
4. 若当前为 root 权限，在命令最末尾追加 `--no-sandbox`；
5. 若用户家目录不可写，在执行当前命令前临时重定向 `HOME=/tmp`；
6. 若 macOS 沙箱崩溃或无输出，立即停止在当前沙箱中盲目重试。

未经用户明确授权，严禁擅自安装系统包或拉取 Docker 容器。

## 桌面 CLI 缺失时的浏览器降级

若本地无桌面客户端但具备 Python 环境，使用包内脚本生成在线编辑链接：

```bash
python3 <this-skill-dir>/scripts/encode_drawio_url.py input.drawio
```
