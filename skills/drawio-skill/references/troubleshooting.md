# Troubleshooting — Common Mistakes

Read this when something looks wrong in the output (rendering, export, layout, edges) or when a CLI invocation fails. Most rows have a one-line fix.

| Mistake | Fix |
|---------|-----|
| Missing `id="0"` and `id="1"` root cells | Always include both at the top of `<root>` |
| Shapes not connected | `source` and `target` on edge must match existing shape `id` values |
| Self-closing edge `mxCell` (`<mxCell ... edge="1" />`) | Use the expanded form with `<mxGeometry relative="1" as="geometry" />` child — self-closing edges won't render |
| `--` inside XML comments | Illegal per XML spec — use single hyphens or rephrase |
| Special characters in `value` | Use XML entities: `&amp;` `&lt;` `&gt;` `&quot;` |
| Literal `\n` in label text | Use `&#xa;` for line breaks in `value` attributes |
| Overlapping shapes | Scale spacing with complexity (200–350px); leave routing corridors |
| Edges crossing through shapes | Add waypoints, distribute entry/exit points, or increase spacing |
| Arrowhead overlaps bend | Final edge segment before target must be ≥20px — increase spacing or add waypoints |
| Iteration loop never ends | After 5 rounds, suggest user open .drawio in draw.io desktop for fine-tuning |
| Export command not found on macOS | Try full path `/Applications/draw.io.app/Contents/MacOS/draw.io` |
| Linux: blank/error output headlessly | Prefix command with `xvfb-run -a` |
| Linux: `--no-sandbox` placed before input file (parsed as filename) | Move `--no-sandbox` to the very end of the command (drawio-desktop#249, #1056) |
| Linux: `Failed to get 'appData' path` / `Home directory not accessible` | `export HOME=/tmp` before invoking drawio (drawio-desktop#127) |
| Linux server: segfault / EGL / MESA `failed to load driver` errors | Add `--disable-gpu` (suppresses Chromium GL init when no GPU available) |
| PDF export fails | Ensure Chromium is available (draw.io bundles it on desktop) |
| Background color wrong in PNG export | Add `--transparent` / `-t` and ensure the source has no canvas-covering background shape. For SVG/PDF rules, read `export.md`. |
| Vision returns 400 "Could not process image" on draft PNG | Re-export the preview without `-e` (issue #8). Root cause is a truncated IEND chunk in `-e` PNGs, not the `zTXt` chunk itself — but skipping `-e` for the preview is the simplest fix. |
| Final `-e` PNG won't open in image viewers / vision APIs | Run `python3 <this-skill-dir>/scripts/repair_png.py <path>`. draw.io CLI emits `-e` PNGs with an 8-byte truncation at IEND. SVG/PDF unaffected. |
| SVG consumer reports `text is not svg` | Embedded draw.io XML, XML/DOCTYPE preambles, `foreignObject`, and per-label fallback images can trip strict sniffers. For PPT/Office, use `scripts/export_ppt_svg.py` and keep the `.drawio` source separately. |
| Fonts change after inserting SVG into PowerPoint | Native SVG `<text>` depends on fonts installed on the presentation machine. Do not fix this by only changing `font-family` or bulk-replacing `html=1`; export text as glyph paths with `scripts/export_ppt_svg.py`. |
| PPT-safe SVG has the wrong glyph style | Path conversion locks whatever font Draw.io used on the export machine. Confirm the requested font is installed there and visually QA the Draw.io/PDF rendering before final export. |
| PDF-to-SVG output has a white background | PDF export adds a page rectangle even when Draw.io shapes use transparent fills. Use `scripts/export_ppt_svg.py`, which removes only the generated clipped white page background and validates the result. |
| Transparent PNG preview appears to lose black text | Some previewers composite alpha over black. Use an opaque temporary PNG for visual QA, then verify the transparent deliverable over its intended slide/page background. |

## PPT/Office-safe SVG with locked fonts

Use this flow when the target is PowerPoint, Office, a strict SVG renderer, or any consumer that substitutes fonts. A normal Draw.io SVG can contain editable diagram XML, XHTML `foreignObject` labels, fallback images, or native `<text>` nodes. Each is valid in some SVG viewers, but none guarantees Office compatibility and identical typography across machines.

Preferred command:

```bash
python3 <this-skill-dir>/scripts/export_ppt_svg.py input.drawio output.svg
```

The script requires Draw.io Desktop and Poppler's `pdftocairo`. It performs this deterministic pipeline:

1. Export the approved Draw.io page to a cropped PDF, using Draw.io's actual font renderer.
2. Convert the PDF to SVG; Poppler represents glyphs as reusable SVG paths instead of `<text>` or `foreignObject`.
3. Remove the single clipped white page rectangle introduced by PDF export, preserving transparent diagram fills.
4. Serialize the document with `<svg>` as the first bytes for strict MIME sniffers.
5. Fail validation if text or `foreignObject` nodes remain.

Before export, ensure the intended font exists on the export host. On Linux, use `fc-match '<font name>'`; the resulting paths faithfully preserve the font actually selected by Draw.io, including an unintended fallback.

Validate the final artifact:

```bash
xmllint --noout output.svg
file --mime-type output.svg
rg -n '<text|foreignObject|fill="rgb\(100%, 100%, 100%\)"' output.svg
```

Expected result: MIME type `image/svg+xml`; the `rg` command prints nothing. Keep `input.drawio` as the editable source because outlined SVG text is no longer editable as text.
