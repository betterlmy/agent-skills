# 样式预设系统：提取、应用与管理

**样式预设（Style Preset）** 是一个结构化的 JSON 文件，用于沉淀用户的视觉偏好——涵盖调色板、形状图形库、字体层级以及连线风格。当一个预设被激活时，它将完全替换 `xml-authoring.md` 中的内置颜色与连线规范。

在以下场景查阅本文档：
- 用户要求从文件或参考图中“学习”、“保存”、“记住”或“提取”样式；
- 用户希望管理已有预设（查看列表、设置默认预设、删除、重命名）；
- 主工作流确定了激活的预设，需要执行具体的应用规则；
- 在加载前对预设 JSON 执行校验。

## 预设存放路径与查找优先级

1. `~/.drawio-skill/styles/<name>.json`：用户自定义预设（在项目拉取或更新时持久保留）；
2. `<this-skill-dir>/styles/built-in/<name>.json`：Skill 随附的内置预设（如 `default`, `corporate`, `handdrawn`）。

同名的用户自定义预设优先级高于内置预设。

仅用户预设允许包含 `"default": true` 标志。当用户说“把某内置预设设为我的默认”时，先将内置 JSON 复制到 `~/.drawio-skill/styles/<name>.json`，再在副本中设置 `default: true`，严禁修改包内内置文件。

**名称规范化**：在读写文件或检索前，始终将用户输入的预设名称统一转换为纯小写。

## 应用样式预设的核心规则

一旦确定了生效的预设，图表的配色板、形状关键字、连线默认值和字体全部遵从该预设，切勿混合使用内置调色板。

**色彩映射逻辑**：对图元扮演的角色（service / database / queue / gateway / error / external / security），按 `preset.roles[role]` 解析到槽位（Slot），再从 `preset.palette[<slot>]` 获取 `(fillColor, strokeColor)` 颜色对。若该角色未定义或对应的槽位为空，按以下梯度回退：

1. 尝试使用角色的规范标准槽位（`service→primary`, `database→success`, `queue→warning`, `gateway→accent`, `error→danger`, `external→neutral`, `security→secondary`）；
2. 若该槽位依然为空，选取预设中被最多节点使用的非空槽位；
3. 严禁回退到系统内置的默认颜色表中，必须保证预设的绝对权威性。

**判断框与容器图元**：
- **判断条件框（菱形）**：使用 `preset.palette.warning` 对应槽位；
- **分组容器（泳道）**：使用与容器所代表的分层对应的槽位（如服务层使用 `primary`，数据层使用 `success`），未明确时默认为 `primary`。

**图元样式前缀**：使用 `preset.shapes[role]` 作为 vertex 样式字符串的前缀（置于 `whiteSpace=wrap;html=1;...` 之前）。

**连线样式**：以 `preset.edges.style` 作为基础样式，并拼接 `preset.edges.arrow`。各连线的具体走线桩位（exitX/entryX 等）依然按 `xml-authoring.md` 添加。若两个形状之间的关联属于可选链路（命中 `preset.edges.dashedFor`），追加 `;dashed=1`。

**字体设置**：在所有 vertex 样式中追加 `fontFamily=<preset.font.fontFamily>;fontSize=<preset.font.fontSize>`。容器大标题当 `preset.font.titleBold` 为 `true` 时，额外配置字阶并加粗。

**附加特性（Extras）**：
- `preset.extras.sketch === true`：在所有节点与连线中追加 `sketch=1` 手绘效果；
- `preset.extras.globalStrokeWidth !== 1`：在所有图元与连线中追加 `strokeWidth=<n>` 边框粗细。

**与图表类型预设的叠加关系**：保持图表类型预设（如 ERD、UML）的骨架样式结构，在此之上覆盖应用当前预设的色彩、字体与连线。类型预设中硬编码的颜色让位于用户预设（但 `fillColor=none` 作为结构性透明设置应予以保留）。

## 样式学习工作流（Learn Flow）

触发语境：“从 `<path>` 学习我的样式并命名为 `<name>`”、“将此保存为 `<name>` 样式预设”。

根据文件后缀分流：
- `.drawio`, `.xml`：走 XML 提取管线；
- `.png`, `.jpg`, `.jpeg`, `.svg`：走图片视觉提取管线。

核心步骤：
1. 阅读 `references/style-extraction.md`；
2. 依据文档流程完成参数提取；
3. 将预设名规范化为纯小写，生成临时候选文件 `/tmp/drawio-preset-<name>.json`（此时先不写入持久目录）；
4. 基于 `style-extraction.md` 中的样本骨架渲染一份样例图，导出不带 `-e` 的纯净预览图 `./preset-<name>-sample.png`；
5. 向用户展示提取摘要（各槽位 Hex 色值、字体、线型）、样例图路径以及置信度评估；
6. 经用户确认满意后，正式落盘至 `~/.drawio-skill/styles/<name>.json` 并清理临时文件；用户要求调整则修改候选后重新预览。

## 日常管理操作

所有管理指令均支持自然语言交互：

| 用户提问 | Agent 执行行为 |
|---|---|
| “列出我的所有样式预设”、“我有哪些样式” | 读取 `~/.drawio-skill/styles/` 与内置目录，以表格输出各预设名称、来源路径、默认状态及置信度 |
| “查看 `<name>` 样式详情” | 美化打印该预设的 JSON 内容及核心特征摘要 |
| “将 `<name>` 设为默认样式” | 在对应的用户预设中将 `default: true` 置位，并清除其余预设的默认标志；若目标为内置预设，先复制到用户目录再设置 |
| “取消默认样式” | 清除所有用户预设中的 `default: true` 标记 |
| “删除 `<name>` 预设” | 必须先向用户确认，确认后删除 `~/.drawio-skill/styles/<name>.json`（禁止直接删除内置预设） |
| “将样式 `<a>` 重命名为 `<b>`” | 重命名对应的 JSON 文件并同步修改文件内部的 `name` 字段 |
