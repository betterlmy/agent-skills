# Brand Page Skeletons

A single canonical sequence is itself a source of sameness. If every brand page is `HERO → MARQUEE → MANIFESTO → GRID → CTA → FOOTER`, then every brand page *is* the same page, no matter how well the colors were chosen.

A landing page argues; a portfolio proves; a lookbook seduces; a studio site demonstrates. Those are four different arguments, so they are four different structures. Pick by what the page has to *do*, then diverge inside it (`references/divergence.md` §3, axis C).

---

## 5.A Landing / Launch — A thing exists, and it must be understood

```
HERO (the engine moment)  →  SPEC BAND (4-col hairline, real numbers)  →
THE ARGUMENT (exploded view · demo · full-page engine — SHOW the thing working)  →
ASYMMETRIC PRODUCT GRID (1.4fr 1fr — never 4 identical cards)  →
TECH / DEPTH (dark-panel inversion, numbered only if the numbering means something)  →
CTA (oversized)  →  FOOTER
```

The load-bearing section is **the argument** — an exploded-view scrub, a live console, a working demo (`page-crafting.md` §5.B). A landing page that only *asserts* quality and never *shows* it is a brochure. If the product is physical or layered, take it apart on scroll.

---

## 5.B Portfolio / Personal — The work is the argument; you are not

```
INTRO (a full-bleed image or a statement — not a headshot-and-tagline)  →
THE WORK (filmstrip accordion · generative grid · list-rows with thumbnails)  →
MANIFESTO (one statement, one column)  →  CAPABILITIES (list, not cards)  →
SELECTED DETAIL (one project, deep)  →  CONTACT (oversized type)  →  FOOTER
```

Rules specific to a personal site:
- **The work comes before the words.** An "About me" section above the first project is a résumé, not a portfolio.
- **A grid of 6 identical project cards is the failure mode.** Reach for a **list with rows** (`64px 1fr auto 90px` + a small thumbnail), a **hover-expand filmstrip** (`page-crafting.md` §3), or a **generative split grid** (§8). The layout should already say what kind of designer you are.
- **No "skills" bar charts.** A percentage on "creativity" is the single cheapest thing a personal page can contain.
- **One project shown deeply beats six shown shallowly.**

---

## 5.C Lookbook / Collection — The mood is the product

```
HERO (split: type | image, ragged)  →  BRAND STATEMENT (dark inversion, one quote, 100vh)  →
HORIZONTAL LOOKBOOK (pinned track, ragged heights, bottom-aligned)  →
MATERIALS (clip-path wipe cards)  →  COLLECTION (gap:2px grid — a spread, not a card wall)  →
ATELIER (1fr 1fr, image + CTA)  →  FOOTER
```

Light/dark alternation is the structure here, which forces a **nav that adapts to what's under it** (`page-crafting.md` §4 — scroll-spy, not `mix-blend-mode`). Density comes from *rhythm* (ragged heights, tight gutters), not from adding sections. Hierarchy is carried by an **opacity ladder on 3-4 tokens**, not by more colors.

---

## 5.D Agency / Studio — The capability is the product

```
HERO (composition — geometric collage · type-as-image · CSS-only)  →
PROOF BAND (stats with real provenance)  →  CRAFT (split, one idea)  →
SERVICES (≤4, and they must differ from each other visually)  →
DARK INVERSION (offers · bento · a change of key)  →
TESTIMONIAL RAIL (scroll-snap, autoplay off on interaction)  →  CTA  →  FOOTER
```

The trap: **services as four identical icon-cards** — icon, title, two lines, ×4. That is the #1 tell (`anti-cheap.md`), and it's endemic to agency pages. If four services must appear, make the cards structurally different (varying spans, one with an image, one with a number), or use a numbered list with real typographic weight instead.

---

## Rules That Hold Across All Four

- **Nav:** single line, ≤80px. Over alternating light/dark sections use a **scroll-spy class toggle** (`page-crafting.md` §4). `mix-blend-mode: difference` only over *high-contrast* imagery — it goes muddy over mid-tones.
- **Layout diversification:** once a layout family is used (3-col cards, full-width quote, split image+text), it appears **at most once more**. Max 2 consecutive image+text zigzags. **A page with 8 sections uses ≥4 layout families** — count them before shipping.
- **Eyebrow restraint:** the tiny-uppercase-tracked label above every headline is the #1 AI tell. Max **1 eyebrow per 3 sections** — `≤ ceil(sections / 3)`, counted, not felt. Usually the headline alone is enough.
- **Theme lock:** one theme per page — *except* where the skeleton above calls for a deliberate dark inversion (5.C, 5.D), which is a structural device, not a drift.
- **Numbering (`01 · 02 · 03`) must be motivated by the material** — film frame codes, plate numbers, movement parts. As default architecture it is a tell.
