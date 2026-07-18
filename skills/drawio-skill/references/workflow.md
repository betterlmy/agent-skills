# Diagram workflow and review loop

Read this file when creating a new diagram, making broad layout changes, or running visual QA. For XML syntax use `xml-authoring.md`; for commands and deliverable modes use `export.md`.

## 1. Confirm the deliverable

Proceed without questions when the request already identifies the subject and output. Otherwise ask only for missing decisions that materially change the result:

- diagram type or purpose;
- required components and relationships;
- output format and destination;
- target consumer, especially Draw.io editing versus PowerPoint/Office;
- fidelity constraints such as transparent background, exact palette, font, aspect ratio, or source-image matching.

Do not ask the user to repeat information visible in an attached diagram or existing `.drawio` file.

## 2. Resolve style

1. If the user clearly names a saved style, load it using `style-presets.md`.
2. Otherwise check `~/.drawio-skill/styles/` for one preset with `"default": true`.
3. If neither applies, use the built-in conventions in `xml-authoring.md` or the relevant structure in `diagram-types.md`.
4. A diagram-type preset supplies structure; a user style preset overrides colors, fonts, edge appearance, and extras.

Do not treat a component name as a style name. For example, “with Redis” identifies content, not a preset.

## 3. Plan before writing XML

- Inventory nodes, containers, edges, labels, and external systems.
- Choose top-to-bottom or left-to-right flow based on the dominant relationship.
- Assign a grid and reserve routing corridors before placing cells.
- Put high-degree hub nodes centrally.
- Use real parent-child containment for visible groups.
- For an existing diagram, preserve IDs and tuned coordinates unless the requested change requires regeneration.

## 4. Generate and validate source

Write or edit `.drawio` XML using `xml-authoring.md`, then run:

```bash
python3 <this-skill-dir>/scripts/validate_drawio.py diagram.drawio
```

Fix structural errors before export. A successful XML parse alone does not prove that edges reference valid cells or contain geometry; the validator checks those invariants.

## 5. Export a clean preview

Read `export.md` and export a PNG without `-e`. Embedded PNG previews can be rejected by vision systems and must not be used for self-check.

Review the preview for:

| Check | Failure signal | Typical correction |
|---|---|---|
| Content | Missing, duplicated, stale, or ambiguous labels | Correct source text before styling |
| Hierarchy | Layers or ownership are hard to scan | Strengthen grouping and title hierarchy |
| Overlap | Shapes, labels, or arrowheads collide | Increase spacing or resize cells |
| Routing | Edges cross unrelated nodes or stack | Add corridors, waypoints, or distinct ports |
| Clipping | Text is cut off or wraps awkwardly | Increase width/height or shorten wording |
| Alignment | Rows and columns drift | Snap coordinates and sizes to the grid |
| Contrast | Text or borders disappear on target background | Test against the intended slide/page background |
| Canvas | Shapes sit off-canvas or padding is uneven | Reposition and use a consistent export border |

Run at most two automatic self-check/fix rounds. If vision is unavailable, perform structural validation and tell the user visual QA was not run.

For transparent deliverables, use an opaque temporary preview for text/layout QA and separately inspect the transparent export over the intended background. Some viewers composite transparency over black and can make valid black labels appear missing.

## 6. Review iteratively

Apply narrow feedback as targeted XML edits:

| Feedback | Edit |
|---|---|
| Change color | Update matching cell `fillColor` / `strokeColor` |
| Change text | Update the matching `value` |
| Move or resize | Update the matching `mxGeometry` |
| Add a node | Add one vertex and place it near related nodes |
| Remove a node | Remove the vertex and all incident edges |
| Add a relationship | Add one edge with valid source, target, and geometry |
| Change overall direction | Regenerate the layout while preserving content |

Overwrite the same preview filename after each revision. After five review rounds, suggest Draw.io Desktop for pixel-level manual tuning.

## 7. Finalize

Choose the final mode from `export.md`:

- editable embedded deliverable;
- clean preview/image deliverable;
- PowerPoint/Office-safe outlined SVG.

Always retain and report the `.drawio` source. Report which checks actually ran, distinguish structural validation from visual QA, and state any environment-dependent risk such as unavailable fonts or skipped rendering.
