# 10. Templates & Variants

本文为按需设计参考，受 SKILL.md 的任务范围、已有项目约束与授权规则约束；只应用当前需求相关项。节号沿用原指南，可通过入口索引定位。代码示例中的相对脚本/资产路径以 Skill 根目录为准。

Every diagram ships in three variants (see `assets/`):

| Variant | File pattern | When to use |
|---|---|---|
| **Minimal light** (default) | `template.html`, `example-<type>.html` | Screenshot-ready. Diagram + title. Warm paper. |
| **Minimal dark** | `template-dark.html`, `example-<type>-dark.html` | Dark mode sites, slides, high-contrast posts. |
| **Full editorial** | `template-full.html`, `example-<type>-full.html` | Long-form posts where the diagram is the hero. |
| **Consultant special** (quadrant only) | `example-quadrant-consultant.html` | BCG/McKinsey-style 2×2 scenario matrix. Clinical sans-serif, white bg, bold blue double-ended axes, named scenario cells. See [type-quadrant.md](type-quadrant.md#consultant-special-2x2-scenario-matrix). |

**Sketchy variant** (optional, applied to any of the above) — see [primitive-sketchy.md](primitive-sketchy.md). SVG turbulence filter wobbles strokes for a hand-drawn feel. Good for essays, not for technical docs.

**Terminal variant** (optional, replaces any of the above) — see [primitive-terminal.md](primitive-terminal.md). `template-terminal.html`, `example-<type>-terminal.html`. Charcoal-black CLI-window chrome, monospace type, one red-orange accent. Good for dev-tool / CLI-product posts and technical social cards; not brand-tokenized, so skip it for onboarded/brand-matched output.

**Animation** (optional presentation layer) — see [animation.md](animation.md). Modes are `none` (default), `reveal`, `step`, and `loop`; motion never changes the static meaning or raises the complexity budget.

### To create a new diagram

1. Copy the variant closest to what you want (`template.html` for minimal, `template-full.html` for cards, `template-motion.html` only when motion is requested).
2. If behavior is load-bearing, choose a semantic pattern; then load the matching `references/type-<name>.md`.
3. Replace the eyebrow, h1, and SVG body. Replace `[diagram-slug]` with the file slug and fill `<title>` / `<desc>`.
4. If motion is requested, load `animation.md`; otherwise keep mode `none` and no script.
5. Run the §9 taste gate.

---
