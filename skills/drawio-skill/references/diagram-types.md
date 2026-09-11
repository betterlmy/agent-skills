# 图表类型结构预设

当用户要求绘制特定类型的图表时，应用下述预设来确定图元形态、结构样式与布局习惯。这些预设定义的是**结构性样式关键字**（如 ERD 的 `shape=table;childLayout=tableLayout`）；用户样式预设（参见 `style-presets.md`）则在此基础上叠加配色、字体、箭头与细节视觉效果。

在以下场景查阅本文档：
- 用户明确提出需要绘制 ERD、UML 类图、时序图、系统架构图、深度学习模型图或流程图；
- 为新图表选择标准图形词汇或排版流向。

## ERD（实体关系图）

| 图元 | 样式声明 | 备注说明 |
|---|---|---|
| 表格容器 | `shape=table;startSize=30;container=1;collapsible=1;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;strokeColor=#6c8ebf;fillColor=#dae8fc;` | 每张表作为一个容器 |
| 字段行 | `shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;fontSize=12;` | 作为表格容器的子节点 |
| 主键列 | 行内文本加粗：`fontStyle=1` | 增加 `PK` 前缀或钥匙图标 |
| 外键关联 | 虚线连线：`dashed=1;endArrow=ERmandOne;startArrow=ERmandOne;` | 使用标准 ER 实体箭头表示基数 |
| 布局流向 | 自上而下（TB），表间距保持约 300px | 垂直聚合关联表 |

## UML 类图

| 图元 | 样式声明 | 备注说明 |
|---|---|---|
| 类模型框 | `swimlane;fontStyle=1;align=center;startSize=26;html=1;` | 三段式结构：类名 / 属性 / 方法 |
| 分割线 | `line;strokeWidth=1;fillColor=none;align=left;verticalAlign=middle;spacingTop=-1;spacingLeft=3;spacingRight=10;rotatable=0;labelPosition=left;points=[];portConstraint=eastwest;` | 用于分隔属性与方法段落 |
| 继承关系 | `endArrow=block;endFill=0;` | 空心三角箭头实线 |
| 接口实现 | `endArrow=block;endFill=0;dashed=1;` | 空心三角箭头虚线 |
| 组合关系 | `endArrow=diamondThin;endFill=1;` | 实心菱形 |
| 聚合关系 | `endArrow=diamondThin;endFill=0;` | 空心菱形 |
| 布局流向 | 自上而下（TB），类间距保持约 250px | 接口置于具体实现类上方 |

## 时序图（Sequence Diagram）

| 图元 | 样式声明 | 备注说明 |
|---|---|---|
| 参与者/对象 | `shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;portConstraint=eastwest;` | 带有垂直虚线的生命线 |
| 同步调用 | `html=1;verticalAlign=bottom;endArrow=block;` | 实线，实心箭头 |
| 异步消息 | `html=1;verticalAlign=bottom;endArrow=open;dashed=1;` | 虚线，开放式开口箭头 |
| 返回响应 | `html=1;verticalAlign=bottom;endArrow=open;dashed=1;strokeColor=#999999;` | 灰色虚线 |
| 激活条 | 位于生命线上的 `shape=umlFrame;whiteSpace=wrap;` | 生命线上的狭长激活框 |
| 布局流向 | 自左向右（LR）排列参与者，间距约 200px | 时间轴自上而下演进 |

## 系统架构图（Architecture Diagram）

| 图元 | 样式声明 | 备注说明 |
|---|---|---|
| 分层/分组 | `swimlane;startSize=30;` | 用于清晰隔离 Client / API / Service / Data 层 |
| 微服务节点 | `rounded=1;whiteSpace=wrap;html=1;` + 层级色 | 按分层匹配统一的主题色 |
| 数据存储 | `shape=cylinder3;whiteSpace=wrap;html=1;` | 数据库圆柱图元 |
| 消息队列/总线 | `rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;` | 黄色系，在星型或中心拓扑中居中布局 |
| API 网关/负载均衡 | `rounded=1;` 搭配标志性强调色 | 橙色系网络入口 |
| 外部第三方系统 | `rounded=1;dashed=1;fillColor=#f5f5f5;strokeColor=#666666;` | 虚线灰底标示外部服务 |
| 布局流向 | 根据层级数量决定 TB 或 LR；超过 4 层优先 TB | 枢纽核心居中放置 |

## 机器学习与深度学习网络结构图

专为学术论文（如 NeurIPS、ICML、ICLR）与技术报告设计的神经网络图元：

| 图元 | 样式声明 | 备注说明 |
|---|---|---|
| 网络层积木 | `rounded=1;whiteSpace=wrap;html=1;` + 类型色 | 核心构建单元 |
| 输入 / 输出 | `fillColor=#d5e8d4;strokeColor=#82b366;` | 绿色系 |
| 卷积 / 池化 | `fillColor=#dae8fc;strokeColor=#6c8ebf;` | 蓝色系 |
| 注意力 / Transformer | `fillColor=#e1d5e7;strokeColor=#9673a6;` | 紫色系 |
| 循环网络 / LSTM / GRU | `fillColor=#fff2cc;strokeColor=#d6b656;` | 黄色系 |
| 全连接（FC） / 线性层 | `fillColor=#ffe6cc;strokeColor=#d79b00;` | 橙色系 |
| 损失函数 / 激活层 | `fillColor=#f8cecc;strokeColor=#b85450;` | 红色/粉色系 |
| 残差跳跃连接 | `dashed=1;endArrow=block;curved=1;` | 虚线弧形连线 |
| 张量维度标注 | 作为第二行文本追加：`value="Conv2D&#xa;(B, 64, 32, 32)"` | 使用 `&#xa;` 换行 |
| 布局流向 | 自上而下（数据流向 TB），层间距约 150px | Encoder 与 Decoder 用泳道容器分组 |

**张量标注约定**：在每个网络层标注输入的张量形态，格式如 `(B, C, H, W)` 或 `(B, T, D)`，置于层名称下方第二行。

## 增强型流程图（Flowchart）

| 图元 | 样式声明 | 备注说明 |
|---|---|---|
| 开始 / 结束 | `ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;` | 绿色圆角端点 |
| 执行处理 | `rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;` | 蓝色处理矩形 |
| 判断决策 | `rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;` | 黄色决策菱形 |
| 输入 / 输出 | `shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;` | 橙色平行四边形 |
| 子流程 | `rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;` + 双线边框 | 紫色系 |
| 条件分支文字 | 决策分支线上必须标注 `value="是"` / `value="否"` | 永远明确标记分支流转 |
| 布局流向 | 主流程 TB，垂直间距约 200px | 决策分支向两侧水平引出，并回归中轴 |
