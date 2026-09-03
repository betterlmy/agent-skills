# agent-skills

[![skills.sh](https://skills.sh/b/betterlmy/agent-skills)](https://skills.sh/betterlmy/agent-skills)
[![GitHub Stars](https://img.shields.io/github/stars/betterlmy/agent-skills?style=flat)](https://github.com/betterlmy/agent-skills/stargazers)
[![GitHub License](https://img.shields.io/github/license/betterlmy/agent-skills)](https://github.com/betterlmy/agent-skills/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/betterlmy/agent-skills)](https://github.com/betterlmy/agent-skills/commits/main)

[中文文档](README.zh-CN.md)

A collection of agent skills maintained by `betterlmy`, covering repository guidance, code engineering, visual design and diagrams, frontend development, browser automation, RAG, and skill development.

## Available Skills

| Skill | Purpose | Install |
| --- | --- | --- |
| [`agents-md-expert`](skills/agents-md-expert/SKILL.md) | Create, review, and improve repository-level `AGENTS.md` instructions | `npx skills add betterlmy/agent-skills --skill agents-md-expert` |
| [`audit-overengineering`](skills/audit-overengineering/SKILL.md) | Audit one or more repositories for evidence-backed deletion, simplification, and native or standard-library replacement opportunities | `npx skills add betterlmy/agent-skills --skill audit-overengineering` |
| [`code-review-skill`](skills/code-review-skill/SKILL.md) | Review architecture, security, performance, code quality, and common bugs across major ecosystems | `npx skills add betterlmy/agent-skills --skill code-review-skill` |
| [`codegraph`](skills/codegraph/SKILL.md) | Index local repositories and analyze symbols, call relationships, impact, and affected tests | `npx skills add betterlmy/agent-skills --skill codegraph` |
| [`diagram-design`](skills/diagram-design/SKILL.md) | Create branded editorial HTML/SVG/PNG diagrams, redraw Draw.io or Mermaid sources, and apply accessible visual design rules | `npx skills add betterlmy/agent-skills --skill diagram-design` |
| [`drawio-skill`](skills/drawio-skill/SKILL.md) | Create, edit, review, validate, and export Draw.io diagrams | `npx skills add betterlmy/agent-skills --skill drawio-skill` |
| [`find-skills`](skills/find-skills/SKILL.md) | Discover and install skills from the open agent skills ecosystem | `npx skills add betterlmy/agent-skills --skill find-skills` |
| [`ip-as-logo`](skills/ip-as-logo/SKILL.md) | Generate simple, cute, personified square character logos with rounded heavy forms and a dominant lower-corner composition | `npx skills add betterlmy/agent-skills --skill ip-as-logo` |
| [`go-dev`](skills/go-dev/SKILL.md) | Guide Go development, review, APIs, concurrency, persistence, and testing from repository constraints and the detected stack | `npx skills add betterlmy/agent-skills --skill go-dev` |
| [`go-auditor`](skills/go-auditor/SKILL.md) | Evidence-driven audits for Go repositories, modules, packages, directories, file sets, hotspots, and diffs | `npx skills add betterlmy/agent-skills --skill go-auditor` |
| [`go-mcp-builder`](skills/go-mcp-builder/SKILL.md) | Build Go MCP servers with `mcp-go` and Streamable HTTP | `npx skills add betterlmy/agent-skills --skill go-mcp-builder` |
| [`mermaid-diagrams`](skills/mermaid-diagrams/SKILL.md) | Create software diagrams with Mermaid, including flowcharts, sequence diagrams, ERDs, and C4 models | `npx skills add betterlmy/agent-skills --skill mermaid-diagrams` |
| [`playwright-cli-cdp`](skills/playwright-cli-cdp/SKILL.md) | Control Chrome-family browsers through CDP with `playwright-cli` | `npx skills add betterlmy/agent-skills --skill playwright-cli-cdp` |
| [`rag-agent-builder`](skills/rag-agent-builder/SKILL.md) | Build RAG applications with embeddings, vector databases, retrieval, and evaluation | `npx skills add betterlmy/agent-skills --skill rag-agent-builder` |
| [`skill-engineer`](skills/skill-engineer/SKILL.md) | Create, improve, review, and evaluate production-ready agent skills | `npx skills add betterlmy/agent-skills --skill skill-engineer` |
| [`simplify-codebase`](skills/simplify-codebase/SKILL.md) | Audit a codebase for evidence-backed simplification, or safely remove accidental complexity with explicit authorization | `npx skills add betterlmy/agent-skills --skill simplify-codebase` |
| [`software-designer`](skills/software-designer/SKILL.md) | Create traceable software design documents from requirements or reverse-engineer them from existing code and evidence | `npx skills add betterlmy/agent-skills --skill software-designer` |
| [`svg-logo-designer`](skills/svg-logo-designer/SKILL.md) | Design and deliver original, scalable, safe, and validated SVG logos and essential variants | `npx skills add betterlmy/agent-skills --skill svg-logo-designer` |

## Installation

Install a skill globally for Codex:

```bash
npx skills add betterlmy/agent-skills --skill <skill-name> -a codex -g -y
```

Install a skill globally for Claude Code:

```bash
npx skills add betterlmy/agent-skills --skill <skill-name> -a claude-code -g -y
```

Omit `--skill <skill-name>` to use the interactive selection provided by the Skills CLI.

## Skill Categories

### Repository and Code Engineering

- `agents-md-expert` keeps repository instructions accurate, scoped, actionable, and verifiable.
- `audit-overengineering` audits one or more repositories for unnecessary abstractions, delegation layers, duplicate capabilities, dead extension points, and replaceable dependencies; it reports evidence-backed candidates without modifying code.
- `code-review-skill` provides cross-language review guidance for architecture, security, performance, quality, and correctness.
- `codegraph` wraps CodeGraph workflows for repository indexing, symbol discovery, call analysis, and change-impact analysis.
- `go-dev` inspects repository constraints and the actual stack before applying Go guidance for code, errors, context, logging, HTTP/gRPC, persistence, concurrency, and testing; response-style preferences are defaults only when the repository is silent.
- `go-auditor` audits Go repositories, modules, packages, directories, file sets, hotspots, and local or revision-based diffs, producing an evidence-driven report with explicit scope boundaries; use `go-dev` to implement fixes.
- `go-mcp-builder` provides a complete workflow for Go MCP servers based on `mark3labs/mcp-go` and Streamable HTTP.

### Design and Diagrams

- `diagram-design` creates branded editorial diagrams as self-contained HTML/SVG/PNG, with templates, accessible SVG checks, and bounded Draw.io/Mermaid redraw workflows.
- `drawio-skill` supports Draw.io architecture diagrams, flowcharts, ER/UML/sequence diagrams, visual QA, and Office-safe export.
- `ip-as-logo` designs the simplest cute IP character logos: compact, recognizable at small sizes, prototyped in batches of six candidates for approval.
- `mermaid-diagrams` covers version-controlled software diagrams using Mermaid syntax.
- `software-designer` creates proportionate Markdown software design documents from requirements or reconstructs as-is designs from code, configuration, schemas, and tests.
- `svg-logo-designer` turns brand briefs into original SVG wordmarks, lettermarks, pictorial marks, combination marks, and essential layout or color variants with structural safety checks.

### Automation and Content

- `playwright-cli-cdp` launches or reuses local Chrome debugging endpoints and drives attached browsers exclusively through CDP.
- `rag-agent-builder` provides examples and utilities for document Q&A, knowledge bases, enterprise search, retrieval, and evaluation.

### Skill Development

- `find-skills` helps identify installable skills for a requested capability.
- `skill-engineer` supports production-oriented skill creation, review, packaging, validation, and realistic evaluation.
- `simplify-codebase` proves consumers and contracts before auditing or, with explicit authorization, removing dead code, duplicate state, redundant layers, obsolete compatibility paths, and other accidental complexity.

## Repository Layout

```text
skills/
  <skill-name>/
    SKILL.md
    agents/       # optional agent metadata
    assets/       # optional reusable assets
    evals/        # optional evaluation cases and results
    examples/     # optional examples
    references/   # optional detailed guidance
    scripts/      # optional executable helpers
    templates/    # optional templates
    tests/        # optional tests
```

Each skill has a `SKILL.md` entry point. Supporting resources are bundled only when the skill needs them; individual skill directories may use different subsets of the optional folders above.

## Related Links

- [Skills routing guide](SKILLS-GUID.md)
- [Skills directory](https://skills.sh/)
- [Skills CLI](https://github.com/vercel-labs/skills)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Claude Code Agent SDK Skills](https://code.claude.com/docs/en/agent-sdk/skills)
