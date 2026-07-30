---
name: drawio-skill
version: 1.6.0
description: Creates, edits, reviews, and exports Draw.io diagrams. Use when the user asks for architecture diagrams, flowcharts, ER/UML/sequence diagrams, .drawio XML changes, diagram visual QA, transparent image export, or PowerPoint/Office-safe SVGs with stable fonts. Do not use for quantitative data charts or requests explicitly requiring Mermaid.
license: MIT
homepage: https://github.com/Agents365-ai/drawio-skill
compatibility: Requires Draw.io Desktop for local rendering; PPT-safe SVG additionally requires Poppler pdftocairo. Vision is optional for visual QA.
external-cli: true
cli-compatibility: references/cli-compatibility.md
platforms: [macos, linux, windows]
metadata: {"openclaw":{"requires":{"anyBins":["draw.io","drawio"]},"emoji":"📐","os":["darwin","linux","win32"],"install":[{"id":"brew-drawio","kind":"brew","formula":"drawio","bins":["draw.io"],"label":"Install draw.io via Homebrew","os":["darwin"]}]},"hermes":{"tags":["drawio","diagram","flowchart","architecture","visualization","uml"],"category":"design","requires_tools":["draw.io"],"related_skills":["mermaid","excalidraw","plantuml"]},"author":"Agents365-ai","version":"1.6.0"}
---

# Draw.io diagrams

Produce editable `.drawio` source first, then export and QA the requested deliverables. Preserve existing diagram tuning during revisions and keep source/editability separate from presentation compatibility.

## Route resources deliberately

Read only the resources needed for the current request:

| Resource | Read when |
|---|---|
| `references/workflow.md` | Creating a diagram, changing layout broadly, or running visual review |
| `references/xml-authoring.md` | Writing or editing Draw.io XML, containers, edges, layout, or transparent fills |
| `references/diagram-types.md` | ERD, UML class, sequence, architecture, ML/DL, or flowchart structure |
| `references/style-presets.md` | Applying, learning, listing, renaming, deleting, or setting a saved style |
| `references/style-extraction.md` | Extracting a style from Draw.io XML or an image |
| `references/export.md` | Exporting PNG/SVG/PDF/JPG or choosing editable versus PPT-safe output |
| `references/troubleshooting.md` | Rendering, CLI, layout, PNG, SVG, font, or background failures |
| `references/cli-compatibility.md` | CLI 版本、必需导出能力或版本漂移 |

Deterministic helpers:

| Script | Purpose |
|---|---|
| `scripts/validate_drawio.py` | Validate root cells, IDs, parents, edge geometry, and references |
| `scripts/repair_png.py` | Repair only the known truncated-IEND form of embedded PNG export |
| `scripts/export_ppt_svg.py` | Create transparent Office-safe SVG with fonts outlined as paths |
| `scripts/encode_drawio_url.py` | Build a client-side diagrams.net URL when Desktop CLI is unavailable |

## Workflow

1. **Confirm scope.** Infer details already present in the prompt, attachment, or source file. Ask only when diagram purpose, required content, output format, destination, or fidelity target would materially change the result.
2. **Resolve style.** Apply a clearly named saved preset; otherwise use the single user preset marked default; otherwise use built-in conventions. A component name is not a style name.
3. **Plan.** Inventory nodes, containers, relationships, labels, direction, grid, and routing corridors before assigning geometry.
4. **Generate or edit.** Follow `xml-authoring.md`. For existing files, make targeted edits and preserve IDs/coordinates unless a layout-wide change requires regeneration.
5. **Validate.** Run `python3 <this-skill-dir>/scripts/validate_drawio.py <file.drawio>` before rendering.
6. **Preview and QA.** Export a PNG without `-e`, inspect it visually when vision is available, and perform no more than two automatic fix rounds.
7. **Review.** Apply user feedback to the existing XML and overwrite the same preview. After five review rounds, suggest Draw.io Desktop for fine tuning.
8. **Finalize.** Choose the correct mode from `export.md`, retain the `.drawio` source, and report actual validation, skipped QA, and environment-dependent risks.

## Non-negotiable source rules

- Include `mxCell` roots `0` and `1`; keep IDs unique per page.
- Escape XML attributes and use `&#xa;` for label line breaks.
- Keep editable labels as `html=1`; do not rewrite source text modes to fix PowerPoint.
- Give every edge an expanded `<mxGeometry relative="1" as="geometry" />` child.
- Use real parent-child containment for grouped content.
- Never use `--` inside XML comments.
- Use `fillColor=none` and no canvas-covering background shape when transparency is required.
- Preserve unrelated user changes and do not overwrite source files outside the requested scope.

## Export decisions

- **Preview:** no `-e`; use a clean PNG for vision and review.
- **Editable final:** use `-e`; use double extensions such as `.drawio.png` or `.drawio.svg` to signal embedded XML.
- **Embedded PNG:** always run `scripts/repair_png.py` after export.
- **PowerPoint/Office or exact fonts:** use `scripts/export_ppt_svg.py`; deliver the `.drawio` source separately because outlined SVG text is not editable.
- **Strict SVG error such as `text is not svg`:** do not strip or mutate labels ad hoc; route to the PPT-safe export and `troubleshooting.md`.

## QA and completion

Before handoff:

- structurally validate the `.drawio` source;
- check content, hierarchy, overlap, clipping, alignment, routing, contrast, and canvas bounds;
- validate final file type/XML where applicable;
- verify PPT-safe SVG contains no `<text>` or `foreignObject` nodes;
- report both source and export paths;
- distinguish structural validation, visual QA, conditional skips, and untested target-environment behavior.

If Draw.io Desktop is unavailable or crashes in a restricted sandbox, stop retrying in the same isolation. Use `scripts/encode_drawio_url.py` or deliver valid `.drawio` XML, and explain which exports still require a host environment.
