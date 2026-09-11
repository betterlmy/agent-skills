---
metadata:
  external-cli: "true"
  cli-compatibility: "references/cli-compatibility.md"
name: finesse-ui
description: 构建绝不廉价的高级网络界面，覆盖品牌页（落地页、品牌站、作品集、hero 引擎页）、产品界面（仪表盘、管理后台、分析看板、数据表格、应用壳、AI 工作台与 agent 控制台）、交易页面（商详、列表、购物车、结算）、H5/移动端页面（活动页、移动商详、报告 H5、app 原型）与单组件精修，并内置反 AI-slop 审计、动效/3D 增强与跨次构建的防趋同旋转。Use when 用户要求构建或改版上述任一页面类型，要求加动效、3D、深度或"让它动起来"，抱怨页面千篇一律、"每次都差不多"、"feels generic"，或明确要求做廉价感/高级感审计。不用于纯后端或数据层逻辑、普通 CSS 缺陷修复、以及不产出界面的任务。
---

# finesse — 技术惊艳 · 灵魂独特 · 绝不廉价

面向四大语境构建高级界面：**品牌（brand）**（视觉张力 + 灵魂表达）、**产品（product）**（信息密度 + 极致清晰）、**交易（commerce）**（混合平衡）、**移动端（h5）**（纯手机容器）。全系通用工艺基线：有色中性灰底色、禁用纯 `#fff`/`#000`、半透明微边框、严苛对比度底线以及色彩锁定。

## 标准工作流程

0. **确定范围**：单组件微调 → [component-scope.md](references/component-scope.md)；纯手机端容器 → [h5-mobile.md](references/h5-mobile.md)。
1. **设计意图解读（§0 Design Read）**：读取 `.finesse/log.json`（[divergence.md](references/divergence.md)），推断所属语境与设计灵魂，输出纯客观可感知的解读报告，并**停下来等待用户明确确认**。
2. **三旋钮设定（§1 Three Dials）**：设定 灵魂（SOUL）· 视觉张力（SPECTACLE）· 信息密度（DENSITY）（预设见 [dial-presets.md](references/dial-presets.md)）。承诺的视觉张力必须在代码中真实呈现。
3. **基底构筑（§3 Substrate）**：铺设通用基底（[design-dna.md](references/design-dna.md)）；按类型分流至品牌基底（[design-dna.md](references/design-dna.md)）、产品基底（[product-ui.md](references/product-ui.md)）或手机端容器（[h5-mobile.md](references/h5-mobile.md)）。
4. **语境路由（Route by Register）**：
   - **品牌（brand）**：选定设计灵魂（[style-personas.md](references/style-personas.md)、[inspiration-catalog.md](references/inspiration-catalog.md)）、5 轴防趋同旋转（[divergence.md](references/divergence.md)）、动效路径（[motion.md](references/motion.md)），以及一种核心渲染引擎（[hero-engines.md](references/hero-engines.md)、[3d-effects.md](references/3d-effects.md)、[page-crafting.md](references/page-crafting.md)）。
   - **产品（product）**：铺设精选中性坡阶（[product-palettes.md](references/product-palettes.md)），而后按需选择浏览类（[product-ui.md](references/product-ui.md)）、操作类（[workflow-ui.md](references/workflow-ui.md)）或控制台委托类（[ai-console.md](references/ai-console.md)）。图表系统参阅 [dataviz.md](references/dataviz.md) 与 [chart-crafting.md](references/chart-crafting.md)。代码范本见 `examples/EXAMPLES.md`。
   - **交易（commerce）**：按商品 SKU 规模在 [commerce-ui.md](references/commerce-ui.md) 中分流。素材搜寻参阅 [asset-sourcing.md](references/asset-sourcing.md)。
5. **骨架选型（§5 Skeleton）**：品牌页从 4 大骨架中选择（[page-skeletons.md](references/page-skeletons.md)）；产品页采用壳层布局；H5 采用移动端专用形态。
6. **起飞前检查（§8 Pre-flight）**：执行反廉价清单（[anti-cheap.md](references/anti-cheap.md)）、移动端底线（[mobile-floor.md](references/mobile-floor.md)）及上线前终检（[preflight.md](references/preflight.md)）。在 CSS 中盖戳并向 `.finesse/log.json` 追加构建记录。

自动化 `audit` 依赖 Node.js 运行 `scripts/detect.mjs`，契约见 [CLI 兼容性契约](references/cli-compatibility.md)；缺失时按 [audit.md](references/audit.md) 人工清单降级。项目配置与规范提取见 [init.md](references/init.md)、[document.md](references/document.md)、[design-model.md](references/design-model.md)；多主题见 [theming.md](references/theming.md)；用户沟通用词见 [plain-words.md](references/plain-words.md)。

## 交互指令集

| 指令 | 参考文档 | 行为与执行范围 |
|---|---|---|
| `craft [brief]` | 全部资源 | 完整设计流水线：意图解读 → 三旋钮 → 基底铺设 → 引擎装配 → 完整组装（默认模式） |
| `audit [target]` | [audit.md](references/audit.md) | **只读**诊断：廉价感扫描与规范预检（绝不修改任何代码） |
| `bolder` / `quieter` | [hero-engines.md](references/hero-engines.md) | 调整视觉张力（SPECTACLE）±2；升级或简化核心视觉引擎 |
| `soul [target]` | [style-personas.md](references/style-personas.md) | 当页面调性与业务不符时，重新挑选设计人设 |
| `diverge [target]` | [divergence.md](references/divergence.md) | 在 5 个正交维度上重构灵魂；强制与 `.finesse/log.json` 历史记录拉开差异 |
| `animate [target]` | [motion.md](references/motion.md) | 用最低性能开销的路径重切动效节拍表；全页限制最多 1 处重量级动效 |
| `depth [target]` | [3d-effects.md](references/3d-effects.md) | 增加 1 处 3D 视觉焦点（优先采用纯 CSS 倾斜/翻转，最后才选 Three.js） |
| `densify [target]` | [product-ui.md](references/product-ui.md) | 调整信息密度（DENSITY）±2 |
| `redesign [target]` | [redesign-mode.md](references/redesign-mode.md) | 渐进式改版升级；按 [iteration-guide.md](references/iteration-guide.md) 映射用户反馈 |

## 核心设计法则

### §0 设计意图解读（直述断言，拒绝低效试探）
读取 `PRODUCT.md`（产品简报）、`design-model.yaml`（设计 Token）以及 `.finesse/log.json`（防趋同历史）。输出格式如下：
```text
Lazy default (rejected): {直接排除的平庸常见方案}
Design Read: {所属行业} · {选定灵魂} · register={brand|product|commerce|h5} · SPECTACLE={1-10} · layout={布局族} · engine={引擎类型}
You'll see: {客观可感知的直观描述 — 色彩、动效节拍、字体层级、界面骨架}
Motion: {动效节拍清单 — 每拍一行客观描述，并注明降级备选；见 motion.md §4}
Images: {图片占位数量、表现形式、素材来源 — 必须先提问确认，严禁擅自生成或抓取未授权素材；见 asset-sourcing.md}
Not right? ① {最可能出现的首要分歧点} ② {次要分歧点}
Rotation: {一句说明本次刻意避开的近期历史方向；见 divergence.md §4}
```
**必须停下来等待用户确认，确认前严禁编写业务代码。** 简报模糊时：只提一个关键问题（[plain-words.md](references/plain-words.md)）。工作台参数判定见 [dial-presets.md](references/dial-presets.md)。

### §1 三旋钮与 §2 灵魂
- **灵魂（SOUL）**（1–10）：极具态度的视觉标识。在 5 个正交维度上重新组合（[divergence.md](references/divergence.md) §3）；相比历史记录必须轮换 ≥3 个维度。
- **视觉张力（SPECTACLE）**（1–10）：渲染引擎野心。产品界面固定在 1–4；品牌页面可达 7–10。硬性规定：若声明 `SPECTACLE ≥ 7`，必须能稳定以 60fps 运行对应引擎，否则降级为 4 档静态高保真方案。
- **信息密度（DENSITY）**（1–10）：单位面积承载的信息量。产品界面固定在 6–9；品牌页面固定在 3–6。

### §3 界面基底与 §4 视觉焦点引擎
- **全系通用基底**：细发丝微边框（`rgba(255,255,255,.07-.22)` / `rgba(0,0,0,.06-.08)`）、有色中性灰阶（严禁纯 `#fff`/`#000`）、严格色彩锁定。
- **品牌界面**：微颗粒胶片噪点（`opacity .025-.05`）、暗角渐变、采用负字距与 `clamp()` 缩放的展示字体、分层 z-index 纵深（[design-dna.md](references/design-dna.md)）。
- **产品界面**：质感操作平面、关键 KPI 磁贴看板、严谨固定字阶、及时细腻的操作反馈动效（[product-ui.md](references/product-ui.md) §0）。绝不使用品牌级胶片噪点与大字标题。
- **核心引擎**：严格只选 1 种（[hero-engines.md](references/hero-engines.md)）：Three.js、Canvas 2D、FBO 粒子着色器、GSAP 时间轴或纯 CSS 动效。必须优雅降级并完整支持 `prefers-reduced-motion`。

### §5 页面骨架模式
品牌类页面从 [page-skeletons.md](references/page-skeletons.md) 的 4 种模式中选择其一：**5.A 落地页（Landing）**、**5.B 作品集（Portfolio）**、**5.C 视觉画册（Lookbook）**、**5.D 创意机构（Agency）**。产品类页面采用 [product-ui.md](references/product-ui.md) 壳层；H5 页面严格遵守 [h5-mobile.md](references/h5-mobile.md)。硬性约束：每 3 个区块最多出现 1 个小眉标（eyebrow）；单行固定导航栏高度 ≤80px 并带滚动监听；每 8 个区块中至少融合 ≥4 种布局形式。

### §6 廉价感黑名单（严厉杜绝）
严禁出现：文案滥用破折号（em-dash）、渐变填充文字、千篇一律的玻璃拟态默认卡片、AI 风格紫蓝荧光、结构完全雷同的 3×2 卡片网格（图标+标题+描述）、虚假的高精度统计数字（如“92%”）、纯 div 拼凑的虚假截图。详细清单见 [anti-cheap.md](references/anti-cheap.md)。

### §7 性能保障与移动端底线
动画属性仅限 transform 和 opacity；严格保障 WCAG AA 级色彩对比度（普通文本 ≥4.5:1，大字 ≥3:1）；交互点击热区 ≥44px。移动端铁律（[mobile-floor.md](references/mobile-floor.md)）：
- M1：全屏横向锁死 `overflow-x: clip`；
- M2：网格列宽严格使用 `minmax(0,1fr)`；
- M3：可点击纯文本禁止折行；
- M4：大标题强制配置 `overflow-wrap: anywhere`；
- M5：移动端仅允许单个置顶吸顶元素（`top: 0`）；
- M6：全大写英文字符 `line-height ≥ 1.0`。纯手机端落地遵守 [h5-mobile.md](references/h5-mobile.md) §10。

### §8 上线前终检与构建归档
执行 [preflight.md](references/preflight.md) 终检清单与 `node scripts/detect.mjs --json`。在输出的 CSS 顶部打上构建戳（`/* finesse · register=... */`），并将本次构建特征追加至 `.finesse/log.json`（[divergence.md](references/divergence.md) §4.1）。交付后的细节微调映射参阅 [iteration-guide.md](references/iteration-guide.md)。

## 不在适用范围内
纯后端或 API 接口开发任务、无设计修饰的原生无样式 UI 需求，以及原生客户端 SDK 集成（如微信 JS-SDK、原生桥接接口、支付 SDK 等）。

---

## 上游来源与授权
本 Skill 适配自 [finesse-skill](https://github.com/mouse-lin/finesse-skill)（MIT License，Copyright (c) 2026 西瓜同学），完整许可文本见本目录 `LICENSE`。
