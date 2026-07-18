# Draw.io XML authoring and layout rules

Read this file when generating or editing `.drawio` XML. Keep source text editable with `html=1`; solve Office font compatibility during export, not by rewriting source labels.

## Minimal document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="drawio" version="26.0.0">
  <diagram name="Page-1">
    <mxGraphModel>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

Required invariants:

- Include root cells `id="0"` and `id="1"` in every diagram page.
- Give every cell a unique ID within its page.
- Make top-level cells children of `1`; nested cells use their real container as `parent`.
- Escape `&`, `<`, `>`, and quotes in attribute values.
- Use `&#xa;` for label line breaks, never a literal `\n`.
- Never put `--` inside XML comments.
- Keep `html=1` for editable source labels. Do not bulk-change it to fix PowerPoint fonts.

## Vertices

```xml
<mxCell id="service" value="API Service&#xa;REST / gRPC"
  style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;"
  vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="180" height="70" as="geometry" />
</mxCell>
```

Common structural styles:

| Element | Style prefix |
|---|---|
| Rectangle | `rounded=0` |
| Rounded service | `rounded=1` |
| Database | `shape=cylinder3` |
| Decision | `rhombus` |
| Start/end | `ellipse` |
| Titled container | `swimlane;startSize=30` |
| External system | `rounded=1;dashed=1` |

Set `fillColor=none` for transparent shapes. A transparent diagram also requires no page/background shape covering the canvas.

## Containers

Use containment rather than placing children visually on top of a large rectangle.

```xml
<mxCell id="platform" value="Platform"
  style="swimlane;startSize=30;container=1;pointerEvents=0;"
  vertex="1" parent="1">
  <mxGeometry x="80" y="80" width="500" height="260" as="geometry" />
</mxCell>
<mxCell id="api" value="API"
  style="rounded=1;whiteSpace=wrap;html=1;"
  vertex="1" parent="platform">
  <mxGeometry x="30" y="60" width="160" height="60" as="geometry" />
</mxCell>
```

Child coordinates are relative to the parent. Add `pointerEvents=0` to visual containers that should not capture child-to-child connections.

## Edges

Every edge must have a non-self-closing geometry child:

```xml
<mxCell id="edge-api-db" value="SQL"
  style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;endArrow=classic;endFill=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;"
  edge="1" parent="1" source="api" target="database">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

For explicit routing:

```xml
<mxGeometry relative="1" as="geometry">
  <Array as="points">
    <mxPoint x="400" y="220" />
  </Array>
</mxGeometry>
```

Routing rules:

- Use orthogonal edges for architecture and flow diagrams unless the style preset says otherwise.
- Pin entry and exit points when a side has multiple connections.
- Space three connections on one side at `0.25`, `0.5`, and `0.75`.
- Keep the last straight segment before an arrowhead at least 20 px long.
- Route long edges through empty corridors, not through unrelated shapes.
- Use `dashed=1` only when it has semantic meaning such as optional, async, or external.

Port positions:

| Side | X | Y |
|---|---:|---:|
| Top center | 0.5 | 0 |
| Right center | 1 | 0.5 |
| Bottom center | 0.5 | 1 |
| Left center | 0 | 0.5 |

## Built-in palette

Use only when no user style preset is active.

| Role | Fill | Stroke |
|---|---|---|
| Service | `#dae8fc` | `#6c8ebf` |
| Database/success | `#d5e8d4` | `#82b366` |
| Queue/decision | `#fff2cc` | `#d6b656` |
| Gateway/API | `#ffe6cc` | `#d79b00` |
| Error/alert | `#f8cecc` | `#b85450` |
| External/neutral | `#f5f5f5` | `#666666` |
| Security | `#e1d5e7` | `#9673a6` |

## Layout

- Snap `x`, `y`, `width`, and `height` to a 10 px grid.
- Start with 200 px horizontal / 150 px vertical gaps for up to five nodes.
- Use about 280 / 200 px for 6–10 nodes and 350 / 250 px above ten nodes.
- Reserve roughly 80 px routing corridors between dense bands.
- Align child centers under parent centers for straight vertical edges.
- Put buses, queues, and other hubs in the middle of their consumer row.
- Group related nodes in consistent rows, columns, or containers.
- Prefer concise two-line labels over shrinking text below readable size.

For ERD, UML, sequence, architecture, ML, and flowchart-specific structure, read `diagram-types.md`. If a style preset is active, preserve these structural keywords while applying the preset's colors, font, edges, and extras.
