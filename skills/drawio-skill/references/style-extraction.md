# 样式提取参考手册

当用户要求提取样式（例如“从 `<path>` 学习我的样式并命名为 `<name>`”）或 Agent 在提取后需要渲染样例图以供确认时，按需加载本文档。

## 样例图骨架（供确认预览）

在提取出候选预设后，使用候选预设的调色板、图元形状、字体和连线渲染该包含 7 个节点的样例图。每个角色恰好出现一次；包含 6 条连线（其中一条虚线），全面检验 `edges.arrow`、`edges.style` 与 `edges.dashedFor` 的生效情况。

**布局结构（自上而下 TB）：**
- 第一行（y=40）：`gateway` 居中（x=340）
- 第二行（y=180）：`security`（x=80）、`service`（x=340）、`queue`（x=600）
- 第三行（y=340）：`database`（x=80）、`external`（x=340）、`error`（x=600）

**模板填充规则 — 替换 XML 中的 `{{...}}` 占位符：**

角色 `R` 的节点样式公式：
`<shapes[R]>;whiteSpace=wrap;html=1;fillColor=<palette[roles[R]].fillColor>;strokeColor=<palette[roles[R]].strokeColor>;fontFamily=<font.fontFamily>;fontSize=<font.fontSize>`
- 若 `extras.sketch=true`，在所有节点与连线样式末尾追加 `;sketch=1`；
- 若 `extras.globalStrokeWidth !== 1`，在所有节点与连线样式末尾追加 `;strokeWidth=<n>`。

连线样式公式：
`<edges.style>;<edges.arrow>`
- 连线走线桩位（`exitX/entryX/...`）直接采用模板中的字面值；
- 连线 15 用于检验 `edges.dashedFor`：
  - 若 `edges.dashedFor` 非空，取其第一项作为连线标签，并追加 `;dashed=1`；
  - 若为空，标签使用 `cross-call` 且不加虚线标记。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="drawio" version="26.0.0">
  <diagram name="Preset Sample">
    <mxGraphModel>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- 第一行: gateway -->
        <mxCell id="2" value="Gateway" style="{{VSTYLE:gateway}}" vertex="1" parent="1">
          <mxGeometry x="340" y="40" width="160" height="60" as="geometry" />
        </mxCell>

        <!-- 第二行: security | service | queue -->
        <mxCell id="3" value="Auth" style="{{VSTYLE:security}}" vertex="1" parent="1">
          <mxGeometry x="80" y="180" width="160" height="60" as="geometry" />
        </mxCell>
        <mxCell id="4" value="Service" style="{{VSTYLE:service}}" vertex="1" parent="1">
          <mxGeometry x="340" y="180" width="160" height="60" as="geometry" />
        </mxCell>
        <mxCell id="5" value="Queue" style="{{VSTYLE:queue}}" vertex="1" parent="1">
          <mxGeometry x="600" y="180" width="160" height="60" as="geometry" />
        </mxCell>

        <!-- 第三行: database | external | error -->
        <mxCell id="6" value="Database" style="{{VSTYLE:database}}" vertex="1" parent="1">
          <mxGeometry x="80" y="340" width="160" height="70" as="geometry" />
        </mxCell>
        <mxCell id="7" value="External API" style="{{VSTYLE:external}}" vertex="1" parent="1">
          <mxGeometry x="340" y="340" width="160" height="60" as="geometry" />
        </mxCell>
        <mxCell id="8" value="Error Sink" style="{{VSTYLE:error}}" vertex="1" parent="1">
          <mxGeometry x="600" y="340" width="160" height="60" as="geometry" />
        </mxCell>

        <!-- 连线 -->
        <mxCell id="10" value="" style="{{ESTYLE}};exitX=0.25;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0" edge="1" parent="1" source="2" target="3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="11" value="" style="{{ESTYLE}};exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0" edge="1" parent="1" source="2" target="4">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="12" value="" style="{{ESTYLE}};exitX=0.75;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0" edge="1" parent="1" source="2" target="5">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="13" value="" style="{{ESTYLE}};exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0" edge="1" parent="1" source="4" target="7">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="14" value="" style="{{ESTYLE}};exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0" edge="1" parent="1" source="4" target="6">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
        <mxCell id="15" value="{{EDGE15_LABEL}}" style="{{ESTYLE}}{{EDGE15_DASH}};exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0" edge="1" parent="1" source="4" target="8">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 渲染与确认闭环

1. 将填入参数后的 XML 写入 `/tmp/drawio-preset-<name>.drawio`；
2. 导出一份不带 `-e` 的干净 PNG：`draw.io -x -f png -s 2 -o <preset-name>-sample.png <tmp>.drawio`；
3. 将图片保存至当前工作目录 `./preset-<name>-sample.png`；
4. 向用户呈现预设摘要表格、图片路径与置信度评估；
5. 获得确认后写入 `~/.drawio-skill/styles/<name>.json` 并清理临时文件。若 CLI 缺失无法渲染，依然展示表格并向用户说明原因，不阻碍基于用户确认的保存。

## 基于 XML 文件的提取流程

输入：`.drawio` 文件路径。输出：候选预设 JSON。完全确定性解析，不依赖模型主观推理。

### 核心步骤

1. **解析文件**：收集所有带有 `style=` 属性的 `<mxCell>`，区分为节点（`vertex="1"`）与连线（`edge="1"`）；
2. **拆解样式标记**：按 `;` 切分样式字符串，识别属性键值对与裸关键字；
3. **提取配色板**：统计所有节点 `(fillColor, strokeColor)` 的出现频次，保留出现频次最高的前 ≤7 个颜色对；
4. **提取形状词汇与语义角色映射**：
   按优先级判定图元类型：`cylinder3 > ellipse > rhombus > swimlane > rounded=1 > rounded=0`。
   随后结合节点的图元类别及其 `value` 标签文本推断语义角色（首项命中即生效）：
   - `cylinder3` → `database`
   - `rhombus` → `decision`
   - `swimlane` → `container`
   - 包含 `dashed=1` 且填充为灰阶（RGB 三通道差值均在 ±16 以内）→ `external`
   - 标签文本匹配 `/queue|bus|kafka|rabbit/i` → `queue`
   - 标签文本匹配 `/gateway|api|lb|load/i` → `gateway`
   - 标签文本匹配 `/auth|login|jwt|oauth/i` → `security`
   - 标签文本匹配 `/error|fail|alert/i` → `error`
   - 其余默认 → `service`

   将最频繁出现的 `(role, color-pair)` 填入该角色的规范调色板槽位：
   `service→primary, database→success, queue→warning, gateway→accent, error→danger, external→neutral, security→secondary`。
   判断条件框与容器图元不计入 `roles`，但其颜色参与通用配色板。
5. **提取字体与连线默认值**：统计出频次最高的字体家族与字阶；统计连线的常见端点形态；若含有多条虚线连线且文案相同，提炼为 `edges.dashedFor`；
6. **提取附加样式**：若任一图元或连线包含 `sketch=1`，标记 `extras.sketch = true`；提取节点边框的平均粗细；
7. **生成来源元数据**：标注来源路径、提取日期与高置信度。

## 基于图像的视觉提取流程

输入：PNG/JPG/SVG 图片文件。输出：候选预设 JSON。基于模型视觉理解，置信度最高为中等（medium）。
前置条件：必须在支持 Vision 能力的多模态环境中运行，否则提示用户提供原始 `.drawio` 文件。
通过色相环（Hue Bands）区间将识别出的高光与主体填充色量化归一至对应语义槽位中。
