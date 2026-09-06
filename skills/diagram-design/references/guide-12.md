# 12. Output

本文为按需设计参考，受 SKILL.md 的任务范围、已有项目约束与授权规则约束；只应用当前需求相关项。节号沿用原指南，可通过入口索引定位。代码示例中的相对脚本/资产路径以 Skill 根目录为准。

Always produce a single self-contained `.html` file:

- Embedded CSS (no external except Google Fonts)
- Inline SVG (no external images)
- Static by default; minimal inline JavaScript only for explicit animation controls/state

Renders correctly in any modern browser. Motion-enabled output must render its complete meaning without JavaScript; under `prefers-reduced-motion: reduce` it shows the complete static frame and hides/disables playback controls.

### Accessible SVG contract

Every diagram is an accessible figure by default:

1. Its `<svg>` carries `role="img"` and `aria-labelledby` naming the diagram's `<title>` and `<desc>`.
2. `<title>` is the first child of `<svg>`, before `<defs>`. Assistive technology may ignore a title placed later.
3. The IDs are prefixed per diagram and variant: `<slug>-title` / `<slug>-desc`, where the slug matches the file (`loop`, `loop-dark`, `loop-full`). Bare `title` / `desc` IDs are banned because two inline diagrams would create duplicate IDs and the second could be announced with the first diagram's name.
4. `<title>` is the short name of the subject — roughly the page `<h1>`, and about 60 characters or fewer.
5. `<desc>` is one sentence stating what the diagram shows in terms a reader needs without the image. Describe the content, not the geometry: “Org chart showing a command center routing work to specialist agents and escalation owners,” not “A box at the top with five boxes below it.” A shape-by-shape narration is worse than no useful description.
6. Decorative-only SVG, such as the specimen glyphs in `assets/icons.html`, carries `aria-hidden="true"` instead. Giving decorative marks accessible names adds noise.

### Exporting to PNG / SVG

When the user asks to export, save, rasterize, or convert a generated diagram to `.png` or `.svg`, load [`references/export.md`](export.md) and follow the procedure there. Both formats deliver the diagram only (the `<svg>` node) — editorial wrappers like cards and headers are dropped by design. Export is **manual** — never produce export files unprompted.

Before invoking Playwright or a browser CLI, read [`references/cli-compatibility.md`](cli-compatibility.md). The standalone Skill does not assume that plugin slash-command files are installed.

For an imported diagram, pixel dimensions come from the `viewBox` × scale factor, so its size decision belongs to §11, not to export. For any diagram that needs an exact frame (an OG card or a 1920×1080 slide image), see [`export.md` § Sizing the export](export.md).
