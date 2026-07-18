# Evaluation record — drawio-skill 1.6.0

Date: 2026-07-16

## Scope

Compared the 1.5.3 frontmatter/workflow with 1.6.0 using `trigger-cases.json`, deterministic script tests, and a real architecture diagram from the active workspace.

## Trigger review

The set contains six should-trigger prompts and four near misses.

| Version | Should-trigger | Should-not-trigger | Notes |
|---|---:|---:|---|
| 1.5.3 | 6/6 | 2/4 | Broad “visualizations” wording could capture quantitative charts and explicit Mermaid requests |
| 1.6.0 | 6/6 | 4/4 | Description adds concrete Draw.io/export triggers and explicit data-chart/Mermaid exclusions |

This is a manual description-level review, not a model-runtime benchmark.

## Forward tests

- Validated a real 42-cell architecture `.drawio` file.
- Exported a PPT-safe SVG to a path containing spaces.
- Confirmed the SVG starts with `<svg`, contains paths, and contains no `<text>` or `foreignObject`.
- Confirmed the PDF-generated white page background was removed.
- Exported an embedded transparent PNG and ran the idempotent repair helper.
- Generated a diagrams.net viewer URL from the real source.
- Visually checked an opaque preview; labels, layout, colors, and routing rendered correctly.
- Observed that a transparent preview with black labels appears empty in viewers that composite alpha over black; added explicit dual-preview guidance.

## Script tests

Covered:

- uncompressed Draw.io XML;
- compressed Draw.io pages;
- missing edge geometry rejection;
- valid embedded PNG no-op;
- known IEND truncation repair;
- unknown PNG corruption rejection.

## Remaining limits

- PPT-safe export requires Draw.io Desktop, Poppler `pdftocairo`, and the intended font on the export host.
- Image-based style extraction still depends on a vision-capable model and remains inference-based.
- Trigger results should be rerun with an actual model harness if the skill is published broadly.
