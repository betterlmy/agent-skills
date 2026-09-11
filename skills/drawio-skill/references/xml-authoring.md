# Draw.io XML 编写与布局规范

在生成或编辑 `.drawio` XML 时阅读本文档。始终保持源码文本标签的 `html=1` 可编辑性；对于 Office 字体渲染兼容性，在导出阶段解决，切勿通过破坏性篡改源码标签文本模式来妥协。

## 最小合法文档结构

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="drawio" version="26.0.0">
  <diagram name="Page-1">
    <mxGraphModel>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

必须遵守的硬性约束：

- 每个图表页面必须包含 `id="0"` 和 `id="1"` 两个根级节点；
- 页面内每个 cell 的 ID 必须全局唯一；
- 顶层元素作为 `1` 的子节点；嵌套元素使用真实的容器作为 `parent`；
- XML 属性中的 `&`、`<`、`>` 以及双引号必须正确转义；
- 标签换行统一使用 `&#xa;`，严禁直接在属性值中插入字面换行符 `\n`；
- XML 注释内部严禁连续出现 `--`；
- 保持可编辑标签的 `html=1` 属性，切勿为了迁就 PowerPoint 批量删除该属性。

## 节点图元（Vertices）

```xml
<mxCell id="service" value="API Service&#xa;REST / gRPC"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;"
  vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="180" height="70" as="geometry" />
</mxCell>
```

常见结构化样式前缀：

| 图元类型 | 样式前缀 |
|---|---|
| 普通矩形 | `rounded=0` |
| 圆角微服务组件 | `rounded=1` |
| 数据库存储 | `shape=cylinder3` |
| 决策条件菱形 | `rhombus` |
| 起始 / 终结端点 | `ellipse` |
| 带标题的分组容器 | `swimlane;startSize=30` |
| 外部第三方系统 | `rounded=1;dashed=1` |

需要透明背景的形状设置 `fillColor=none`。透明图表同时要求画布底面不得放置全屏纯色遮挡块。

## 分组容器（Containers）

使用真实的容器包含关系（Containment），而不是单纯在大矩形上面叠放小节点。

```xml
<mxCell id="platform" value="Platform"
  style="swimlane;startSize=30;container=1;pointerEvents=0;"
  vertex="1" parent="1">
  <mxGeometry x="80" y="80" width="500" height="260" as="geometry" />
</mxCell>
<mxCell id="api" value="API"
  style="rounded=1;whiteSpace=wrap;html=1;"
  vertex="1" parent="platform">
  <mxGeometry x="30" y="60" width="160" height="60" as="geometry" />
</mxCell>
```

子节点的坐标相对于其父容器。若容器不应拦截子节点之间的连线点击，添加 `pointerEvents=0` 样式。

## 连接线（Edges）

每条连线必须包含非自闭合的几何属性子标签：

```xml
<mxCell id="edge-api-db" value="SQL"
  style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;"
  edge="1" parent="1" source="api" target="database">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

若需要显式指定连线折点（Waypoints）：

```xml
<mxGeometry relative="1" as="geometry">
  <Array as="points">
    <mxPoint x="400" y="220" />
  </Array>
</mxGeometry>
```

布线设计原则：

- 架构图与流程图统一采用正交连线（orthogonal），除非用户样式预设另有规定；
- 当一个节点的某一边引出或接入多条连线时，显式固定进出桩位（exitX/exitY/entryX/entryY）；
- 若同侧有 3 条连线，均匀分布在 `0.25`、`0.5` 和 `0.75` 处；
- 确保连线终点在接入目标前保留至少 20px 的直线延伸段，防止箭头在转角折线处产生畸变重叠。
