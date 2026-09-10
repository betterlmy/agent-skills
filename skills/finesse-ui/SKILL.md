---
metadata:
  external-cli: "true"
  cli-compatibility: "references/cli-compatibility.md"
name: finesse-ui
description: 构建绝不廉价的高级网络界面，覆盖品牌页（落地页、品牌站、作品集、hero 引擎页）、产品界面（仪表盘、管理后台、分析看板、数据表格、应用壳、AI 工作台与 agent 控制台）、交易页面（商详、列表、购物车、结算）、H5/移动端页面（活动页、移动商详、报告 H5、app 原型）与单组件精修，并内置反 AI-slop 审计、动效/3D 增强与跨次构建的防趋同旋转。Use when 用户要求构建或改版上述任一页面类型，要求加动效、3D、深度或"让它动起来"，抱怨页面千篇一律、"每次都差不多"、"feels generic"，或明确要求做廉价感/高级感审计。不用于纯后端或数据层逻辑、普通 CSS 缺陷修复、以及不产出界面的任务。
---

# finesse — Technically Spectacular · Soul-Distinct · Never Cheap

Builds interfaces across four registers: **brand** (spectacle + soul), **product** (density + clarity), **commerce** (hybrid), and **h5** (phone-only container). Universal craft floor: tinted neutrals, no `#fff`/`#000`, translucent borders, contrast floor, and color lock.

## Workflow

0. **Scope**: Single element → [component-scope.md](references/component-scope.md); phone-only container → [h5-mobile.md](references/h5-mobile.md).
1. **Design Read (§0)**: Read `.finesse/log.json` (`divergence.md`), infer register + soul, output plain observable readout, and **wait for confirmation**.
2. **Three Dials (§1)**: Set SOUL · SPECTACLE · DENSITY (presets in [dial-presets.md](references/dial-presets.md)). Spectacle claimed must be spectacle shown.
3. **Substrate (§3)**: Lay universal floor (`design-dna.md`); fork into brand substrate (`design-dna.md`), product substrate (`product-ui.md`), or phone frame (`h5-mobile.md`).
4. **Route by Register**:
   - **brand**: Pick soul (`style-personas.md`, `inspiration-catalog.md`), 5-axis rotation (`divergence.md`), motion routes (`motion.md`), and one engine (`hero-engines.md`, `3d-effects.md`, `page-crafting.md`).
   - **product**: Neutral ramp (`product-palettes.md`), then read (`product-ui.md`), operate (`workflow-ui.md`), or delegate (`ai-console.md`). Charts: [dataviz.md](references/dataviz.md), [chart-crafting.md](references/chart-crafting.md). Samples: `examples/EXAMPLES.md`.
   - **commerce**: Route by SKU count via [commerce-ui.md](references/commerce-ui.md). Assets: [asset-sourcing.md](references/asset-sourcing.md).
5. **Skeleton (§5)**: Brand uses 4 skeletons ([page-skeletons.md](references/page-skeletons.md)); product uses shell layout; H5 uses mobile morphology.
6. **Pre-flight (§8)**: Run [anti-cheap.md](references/anti-cheap.md), [mobile-floor.md](references/mobile-floor.md), and [preflight.md](references/preflight.md). Stamp CSS and append `.finesse/log.json`.

自动化 `audit` 依赖 Node.js 运行 `scripts/detect.mjs`，契约见 [CLI 兼容性](references/cli-compatibility.md)；缺失时按 [audit.md](references/audit.md) 人工清单降级。项目配置与规范提取见 [init.md](references/init.md)、[document.md](references/document.md)、[design-model.md](references/design-model.md)；多主题见 [theming.md](references/theming.md)；用户沟通用词见 [plain-words.md](references/plain-words.md)。

## Commands

| Command | Reference | Action |
|---|---|---|
| `craft [brief]` | all | Full pipeline: Design Read → Dials → substrate → engine → assemble (default) |
| `audit [target]` | [audit.md](references/audit.md) | **Read-only** diagnostic: cheapness scan + preflight check (changes nothing) |
| `bolder` / `quieter` | [hero-engines.md](references/hero-engines.md) | Adjust SPECTACLE ±2; upgrade or simplify visual engine |
| `soul [target]` | [style-personas.md](references/style-personas.md) | Re-pick persona when page tone is mismatched |
| `diverge [target]` | [divergence.md](references/divergence.md) | Recompose soul on 5 axes; enforce difference from `.finesse/log.json` |
| `animate [target]` | [motion.md](references/motion.md) | Re-cut beat sheet with cheapest routes; limit to 1 heavy beat |
| `depth [target]` | [3d-effects.md](references/3d-effects.md) | Add one 3D moment (default CSS tilt/flip before Three.js) |
| `densify [target]` | [product-ui.md](references/product-ui.md) | Adjust DENSITY ±2 |
| `redesign [target]` | [redesign-mode.md](references/redesign-mode.md) | Iterative upgrades; map feedback via [iteration-guide.md](references/iteration-guide.md) |

## Core Disciplines

### §0 Design Read (Assert, Don't Poll)
Read `PRODUCT.md` (locked brief), `design-model.yaml` (tokens), and `.finesse/log.json` (rotation memory). Output format:
```
Lazy default (rejected): {obvious aesthetic}
Design Read: {industry} · {soul} · register={brand|product|commerce|h5} · SPECTACLE={n} · layout={family} · engine={type}
You'll see: {plain observable terms — color, motion, type size, structure}
Motion: {beat sheet — 1 plain line per beat, plus still fallback; motion.md §4}
Images: {slot count, depiction, session source — ask first, never generate/fetch unprompted; asset-sourcing.md}
Not right? ① {first likely objection} ② {second likely objection}
Rotation: {sentence naming recent directions deliberately avoided; divergence.md §4}
```
**STOP and wait for user confirmation before writing code.** Ambiguous brief: ask ONE question ([plain-words.md](references/plain-words.md)). Workbench resolver in [dial-presets.md](references/dial-presets.md).

### §1 Three Dials & §2 Soul
- **SOUL** (1–10): Opinionated identity. Recompose across 5 orthogonal axes ([divergence.md](references/divergence.md) §3); rotate ≥3 axes from past builds.
- **SPECTACLE** (1–10): Engine ambition. Product pins 1–4; brand reaches 7–10. Mandatory: `SPECTACLE ≥ 7` MUST render 60fps running engine, or drop to 4 static.
- **DENSITY** (1–10): Information density. Product pins 6–9; brand 3–6.

### §3 Substrate & §4 Hero Engine
- **Universal Floor**: Hairline borders (`rgba(255,255,255,.07-.22)` / `rgba(0,0,0,.06-.08)`), tinted neutrals (no `#fff`/`#000`), color lock.
- **Brand**: Grain (`opacity .025-.05`), vignette, `clamp()` display type with negative tracking, layered z-index depth ([design-dna.md](references/design-dna.md)).
- **Product**: Premium surfaces, KPI tiles, fixed type scale, feedback motion ([product-ui.md](references/product-ui.md) §0). No brand grain/hero text.
- **Engine**: Pick ONE ([hero-engines.md](references/hero-engines.md)): Three.js, Canvas 2D, FBO shader, GSAP, or CSS-only. Must degrade gracefully and implement `prefers-reduced-motion`.

### §5 Page Skeletons
Brand selects one from [page-skeletons.md](references/page-skeletons.md): **5.A Landing**, **5.B Portfolio**, **5.C Lookbook**, or **5.D Agency**. Product uses [product-ui.md](references/product-ui.md) shells; H5 uses [h5-mobile.md](references/h5-mobile.md). Restraints: max 1 eyebrow per 3 sections, single-line nav ≤80px with scroll-spy, and ≥4 layout families per 8 sections.

### §6 Cheapness Blacklist
Banned: em-dashes in copy, gradient text, glassmorphism defaults, AI-purple glow, identical card grids (icon+title+text × 6), fake precision numbers (`92%`), div-based fake screenshots. Details in [anti-cheap.md](references/anti-cheap.md).

### §7 Performance & Mobile Floor
Animate transform/opacity only; WCAG AA contrast (≥4.5:1 / ≥3:1); touch targets ≥44px. Hard mobile rules ([mobile-floor.md](references/mobile-floor.md)): M1 `overflow-x: clip`; M2 grid `minmax(0,1fr)`; M3 clickable text no wrap; M4 headings `overflow-wrap: anywhere`; M5 single sticky at `top: 0`; M6 all-caps `line-height ≥ 1.0`. Phone-only builds follow [h5-mobile.md](references/h5-mobile.md) §10.

### §8 Pre-Flight & Build Recording
Run [preflight.md](references/preflight.md) checklist and `node scripts/detect.mjs --json`. Stamp CSS (`/* finesse · register=... */`) and append to `.finesse/log.json` ([divergence.md](references/divergence.md) §4.1). Post-delivery tweaks map via [iteration-guide.md](references/iteration-guide.md).

## Out of Scope
Pure backend/API tasks, unstyled raw UI requests, and native app platform wiring (WeChat JS-SDK, native bridges, payment SDKs).

---

## 上游来源与授权
本 Skill 适配自 [finesse-skill](https://github.com/mouse-lin/finesse-skill)（MIT License，Copyright (c) 2026 西瓜同学），完整许可文本见本目录 `LICENSE`。
