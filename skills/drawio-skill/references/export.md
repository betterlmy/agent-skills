# Export modes, commands, and fallbacks

Read this file whenever an image/PDF/SVG deliverable is requested or Draw.io CLI behavior matters.

## Choose the mode first

| Mode | Use when | Embedded edit data | Font behavior |
|---|---|---:|---|
| Preview PNG | Visual QA and review | No | Rasterized |
| Editable PNG/SVG/PDF | User wants to reopen the export in Draw.io | Yes, with `-e` | Renderer-dependent for SVG |
| PPT/Office-safe SVG | PowerPoint, strict SVG consumer, exact cross-machine typography | No; keep `.drawio` separately | Glyphs outlined as paths |

Do not promise one SVG can be both maximally editable and maximally compatible with Office. Deliver the `.drawio` source alongside a presentation-safe SVG when both needs exist.

## Dependencies

Find Draw.io Desktop using `draw.io`, `drawio`, the macOS application path, or the Windows installation path. On Linux headless hosts, prefer `xvfb-run` and append `--disable-gpu`. If running as root, append `--no-sandbox` at the end of the Draw.io command.

PPT-safe SVG additionally requires Poppler's `pdftocairo` on `PATH` and the intended fonts installed on the export host.

## Preview PNG

Do not use `-e`:

```bash
draw.io -x -f png -s 2 -b 10 -o diagram.png input.drawio
```

Linux headless:

```bash
xvfb-run -a --server-args="-screen 0 1920x1080x24" \
  draw.io -x -f png -s 2 -b 10 -o diagram.png input.drawio --disable-gpu
```

Keep the review preview opaque so black text remains visible in vision tools that composite alpha over black. When transparency itself must be verified, export a second PNG with `-t` and inspect it over the intended slide/page background. For SVG, transparency comes from the source canvas and fills.

## Editable final exports

```bash
draw.io -x -f png -e -t -s 2 -b 10 -o diagram.drawio.png input.drawio
python3 <this-skill-dir>/scripts/repair_png.py diagram.drawio.png

draw.io -x -f svg -e -b 10 -o diagram.drawio.svg input.drawio
draw.io -x -f pdf -e -b 10 -o diagram.drawio.pdf input.drawio
```

Use double extensions to signal embedded diagram data. After every `-e` PNG export, run `repair_png.py`; it validates the PNG signature and repairs only the known truncated-IEND form.

Embedded SVG may contain Draw.io XML, XHTML `foreignObject`, font fallbacks, or images. It is suitable for Draw.io round-tripping but can be rejected by strict consumers.

## PPT/Office-safe SVG

```bash
python3 <this-skill-dir>/scripts/export_ppt_svg.py input.drawio diagram.svg
```

This deterministic pipeline exports Draw.io to cropped PDF, converts PDF glyphs to SVG paths, removes the generated white PDF page rectangle, and writes an SVG whose first bytes are `<svg`.

Before running it, verify the intended font is installed. On Linux:

```bash
fc-match 'Noto Sans CJK SC'
```

The script locks the font Draw.io actually selected, including an unintended fallback. Visually QA the preview before final export.

## Structural and format checks

```bash
python3 <this-skill-dir>/scripts/validate_drawio.py input.drawio
xmllint --noout output.svg
file --mime-type output.svg
```

For a PPT-safe SVG, also verify that no editable text or XHTML remains:

```bash
rg -n '<text|foreignObject' output.svg
```

Expected: no matches. Do not reject `<image>` globally because a diagram may intentionally contain raster assets.

## CLI failure handling

Use this order:

1. Verify the binary with `draw.io --version` or `drawio --version`.
2. On Linux, retry under `xvfb-run -a`.
3. Append `--disable-gpu`.
4. If root, append `--no-sandbox` at the end.
5. If the home directory is inaccessible, set a writable temporary home for that invocation.
6. If a macOS sandbox crashes or returns no output, stop retrying inside that sandbox.

Do not install system packages or start containers without the user's authorization.

## Browser fallback

If the desktop CLI is unavailable but Python exists:

```bash
python3 <this-skill-dir>/scripts/encode_drawio_url.py input.drawio
```

The diagram is encoded in the URL fragment and opens client-side. If Python is also unavailable, deliver only valid `.drawio` XML and explain how to open it manually.

If `pdftocairo` is unavailable for a PPT-safe request, deliver `.drawio` plus PDF or an ordinary SVG with an explicit font-compatibility warning. Do not claim fonts are locked.
