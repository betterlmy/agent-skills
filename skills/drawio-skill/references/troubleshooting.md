# 故障排查与高频避坑指南

当产物出现渲染异常、导出失败、排版错位、连线畸变或 CLI 报错时查阅本文档。绝大部分问题可通过一行操作快速修复。

| 故障现象 | 针对性修复方案 |
|---|---|
| 缺少 `id="0"` 和 `id="1"` 根节点 | 始终在 `<root>` 顶部显式包含这两个根元素 |
| 图元之间连线断开未连接 | 连线上的 `source` 与 `target` 属性必须精确匹配现有图元的 `id` |
| 连线使用了自闭合 `mxCell`（如 `<mxCell ... edge="1" />`） | 必须使用包含 `<mxGeometry relative="1" as="geometry" />` 子标签的完整展开形式，否则渲染引擎无法识别 |
| XML 注释内出现 `--` 字符 | 违反 XML 标准规范，应替换为单短横线或调整表述 |
| `value` 属性中包含特殊字符 | 必须进行 XML 实体转义：`&amp;` `&lt;` `&gt;` `&quot;` |
| 标签文本中直接写了字面 `\n` | 属性中的文本换行统一使用 `&#xa;` |
| 图元互相重叠穿插 | 根据复杂度拉大节点间距（建议 200–350px），并预留连线通道走廊 |
| 连线直接横穿不相干图元 | 添加折点（Waypoints）、分散进出端口（Ports）或调整图元相对距离 |
| 箭头与转折角重叠变形 | 连线在接入目标节点前的最后一段直线长度必须 ≥20px |
| 审查反复迭代无法收敛 | 迭代超过 5 轮后，建议用户直接在 Draw.io Desktop 客户端中手工微调 |
| macOS 下提示找不到导出命令 | 尝试使用绝对路径 `/Applications/draw.io.app/Contents/MacOS/draw.io` |
| Linux 无头模式下输出全黑或报错 | 在命令前添加前缀 `xvfb-run -a` |
| Linux 提示找不到文件名 | `--no-sandbox` 参数必须严格放置在命令的最末尾 |
| Linux 提示无法获取 appData 路径 | 在调用命令前执行 `export HOME=/tmp` |
| Linux 报驱动加载错误或段错误（segfault） | 增加 `--disable-gpu` 参数禁用 GPU 硬件加速 |
| 导出的 PNG 背景颜色异常 | 增加 `--transparent` / `-t`，并确认源码中未放置全屏底色块 |
| 视觉模型读取草稿 PNG 报 400 错误 | 导出预览图时移除 `-e` 参数，以规避内嵌 XML 时已知的 IEND 块截断 |
| 最终 `-e` PNG 在外部看图工具中打不开 | 运行 `python3 <this-skill-dir>/scripts/repair_png.py <path>` 修复文件尾 |
| 第三方工具解析 SVG 报 `text is not svg` | 属于严格 XML 校验拦截，改用 `scripts/export_ppt_svg.py` 导出矢量轮廓图 |
| 将 SVG 插入 PowerPoint 后字体发生变化 | 原生 SVG `<text>` 依赖目标机器已安装字体，使用 `scripts/export_ppt_svg.py` 将文字轮廓化为绝对矢量路径 |
| PDF 转 SVG 后自带纯白背景底板 | 运行 `scripts/export_ppt_svg.py`，它会自动剔除 PDF 生成的白底背景块并保留图表透明度 |
| 透明 PNG 预览图中的黑色文字看似“消失” | 部分查看器将透明通道与黑底混合，应先用不透明预览图质检，再在目标幻灯片背景上实测透明图 |

## 锁定字体的 PPT / Office 安全矢量导出

当目标场景为 PowerPoint、Office 办公套件、严格的 SVG 渲染器或任何容易引发字体替换的环境时，必须采用本流程。

标准执行命令：

```bash
python3 <this-skill-dir>/scripts/export_ppt_svg.py input.drawio output.svg
```

该工具通过以下确定性流水线运作：
1. 调用 Draw.io Desktop 将指定图表页面导出为紧凑裁剪的 PDF；
2. 借助 Poppler 的 `pdftocairo` 将 PDF 中的文字图元转换为可复用的 SVG 闭合矢量路径，杜绝任何 `<text>` 或 `<foreignObject>` 标签；
3. 精准剔除 PDF 导出阶段引入的白色页面矩形，完整保留图表自身的透明填充；
4. 保证输出文件以标准 `<svg>` 开头，兼容各类严苛的 MIME 嗅探器；
5. 执行自动化断言：一旦发现遗留文本标签立即拦截报错。

导出前确保宿主机器已安装对应字体（在 Linux 下可用 `fc-match '<字体名>'` 检查）。请始终保留 `input.drawio` 作为可编辑源文件，因为轮廓化后的矢量路径在后续无法再作为纯文本直接修改。
