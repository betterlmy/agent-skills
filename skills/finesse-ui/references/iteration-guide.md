# Post-Delivery Iteration Guide

After the user receives the initial output, map their feedback to the correct targeted fix. **Never rebuild from scratch for a single complaint** — identify the dial or module responsible and adjust only that.

The **Command** column is the verb to route through; if the user typed the command, you're already there.

| User says | Command | Action |
|-----------|---------|--------|
| "too plain / boring" | `bolder` | Raise SPECTACLE +2; consider upgrading the engine type (e.g. Canvas → Three.js) |
| "too flashy / overwhelming" | `quieter` | Lower SPECTACLE −2; simplify or swap to Engine D (GSAP) or E (CSS-only) |
| "wrong vibe / feels off" | `soul` | Re-run §2 with a different persona from `references/style-personas.md` |
| "too much whitespace" | `densify` | Raise DENSITY +2; add one content section |
| "too cluttered" | `densify` | Lower DENSITY −2; cut a section, increase section padding |
| "more personality / bolder" | `bolder` | Raise SOUL +2; push color commitment level up one step in `references/design-dna.md` |
| "feels generic / like every other AI site" | `diverge` | **Systemic, not per-page.** Recompose the soul from the five axes (`divergence.md` §3), run the two-altitude anti-default check (§2), roll against the argmax (§6), check the used-list (§4). Reaching for `soul` here just picks a *different* row from the same ten-row table — which is the problem, not the fix |
| "every page you make looks the same" | `diverge` | Same as above. Then **write the used-list** (`divergence.md` §4) — without it, "don't repeat" is a rule with no memory behind it and it will never fire |
| "change the colors" | `soul` | Re-run color strategy in `references/design-dna.md`; maintain the accent lock rule |
| "different animation" | `animate` | Swap engine type in §4; re-run `references/hero-engines.md` for that engine's skeleton |
| "add depth / make it 3D / tilt / parallax" | `depth` | Add **one** 3D moment from `references/3d-effects.md` — default to the CSS tier (tilt/flip/coverflow/depth-parallax); Three.js only for a real rendered object |
| "remove a section" | `redesign` | Remove it, then re-audit §5 layout families (ensure ≥4 families remain) |
| "feels slow / heavy" | `quieter` | Lower SPECTACLE; switch to Engine E (CSS-only) or reduce particle count/FBO resolution |
| "needs to work on mobile" | `redesign` | Declare mobile layout per multi-column section; `min-h-dvh`, touch targets ≥44px |
| "不知道它在干嘛 / 一直转圈 / 停不下来 / 花了多少钱看不到" *(AI 工作台)* | `redesign` | Not a styling complaint — the register's four questions are unanswered. `ai-console.md`: a run stream with per-step duration (§2) instead of one spinner, all nine run states (§3), a resident stop (§4), a receipt line and budget meter (§6) |
| "像个聊天窗口，不像工作台" *(AI 工作台)* | `redesign` | Bubbles-only is the failure. `ai-console.md` §1 — the queue and the history are missing, so only the present tense is on screen; add the rail (or the phone's pinned strip, §9) before touching anything visual |
| "刘海挡住了 / 底部栏遮住内容 / 按不动" *(h5)* | `redesign` | Not a layout opinion — a mechanical defect. Run `h5-mobile.md` §10's gates in order: missing `env()` (§2.A), missing `#app` bottom padding (§2.C), sub-44px hit areas or absent `:active` (§3) |
| "不像 app / 像个网页" *(h5)* | `redesign` | The furniture is missing or wrong, not the palette. `h5-mobile.md` §5 — status bar, TabBar active state, home indicator, sheet grab handle, push transition — plus §9's tell list |
| "is this any good? / review it" | `audit` | Read-only: run the blacklist + spectacle-shown + pre-flight, report findings |
