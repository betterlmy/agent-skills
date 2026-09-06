# 4. Universal Anti-patterns

本文为按需设计参考，受 SKILL.md 的任务范围、已有项目约束与授权规则约束；只应用当前需求相关项。节号沿用原指南，可通过入口索引定位。代码示例中的相对脚本/资产路径以 Skill 根目录为准。

These mark "AI slop" schematics of any type:

| Anti-pattern | Why it fails |
|---|---|
| Dark mode + cyan/purple glow | Looks "technical" without design decisions |
| JetBrains Mono as blanket "dev" font | Mono is for *technical* content — ports, commands, URLs. Names go in Geist sans. |
| Identical boxes for every node | Erases hierarchy |
| Legend floating inside the diagram area | Collides with nodes |
| Arrow labels with no masking rect | Bleeds through the line |
| Vertical `writing-mode` text on arrows | Unreadable |
| 3 equal-width summary cards as default | Generic grid — vary widths |
| Shadow on any element | Shadows are out. Borders are in. |
| `rounded-2xl` on boxes | Max radius 6–10px or none |
| Coral on every "important" node | Coral is 1–2 editorial accents, not a signaling system |
| Reproducing Mermaid's renderer layout | Imports automatic spacing and routing instead of making an editorial layout |
| Diagonal / slanted connectors between off-axis nodes | Rounded right-angle (orthogonal) elbows are mandatory — see §6 Mandatory connector rules |
| Arrow label sitting on or touching its connector | Label must have a 6–10px gap above the line so the connector stays visible |
| Arrow label mask overlapping a node box | Nodes paint after labels — the fill clips the text into a fragment on the border. See §6 rule 6 |
| Two connectors overlapping or running on the same path | Each connection must be independently traceable — bridge crossings, offset parallels |
| Two connectors sharing a single attach point on a box | Fan attach points along the edge (≥12px apart) so every arrow is clearly distinct — see §6 rule 4 |
| Connector routed behind a non-endpoint box without need | Reroute around intervening boxes; the dashed-transit exception (§6 rule 5) only applies when an unavoidable intervening box sits on the direct path |

Type-specific anti-patterns live in each `references/type-*.md`.

---
