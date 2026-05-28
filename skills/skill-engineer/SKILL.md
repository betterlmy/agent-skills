---
name: skill-engineer
description: Create, improve, and review production-ready agent skills with concise structure, strong trigger descriptions, bundled resources, validation, and realistic forward testing. Use when the user wants to write a new skill, make an existing skill production-ready, audit or review a skill, compare skill-creator approaches, or decide whether a skill needs scripts, references, assets, metadata, packaging, or evaluation.
---

# Skill Engineer

## Operating Mode

First classify the request:

1. **Create**: user wants a new skill.
2. **Review**: user wants an existing skill audited.
3. **Improve**: user has a draft or installed skill and wants it production-ready.
4. **Evaluate**: user asks whether a skill actually works better than no skill or an older version.

For create/improve work, prefer the host's official skill initializer when one exists. In Codex, default new user skills to `${CODEX_HOME:-$HOME/.codex}/skills` unless the user names another path. For review-only work, do not edit until the user asks for changes or the issue is clearly meant to be fixed.

## Production Standard

A production-ready skill is:

- **Discoverable**: frontmatter `description` names both capability and concrete trigger contexts.
- **Small by default**: keep `SKILL.md` close to 100 lines when practical; split rare or detailed material into one-level `references/` files.
- **Operational**: deterministic or repeated work lives in `scripts/`; reusable output material lives in `assets/`.
- **Portable**: avoid private paths, time-sensitive facts, hidden environment assumptions, and tool names that are not actually available.
- **Validated**: run available validators and the bundled static audit script.
- **Forward-tested**: important skills are tried on realistic prompts, preferably against a no-skill or previous-version baseline.

## Create Workflow

1. Capture concrete use cases before writing.
   Ask only for missing information: task/domain, trigger phrases, expected outputs, required tools, reference material, and whether tests matter.
2. Name the skill with lowercase letters, digits, and hyphens. Prefer action or role names, for example `review-api-contracts` or `skill-engineer`.
3. Draft a pushy but accurate description:
   - First sentence: what the skill does.
   - Second sentence: "Use when..." with triggers, file types, domains, and user intents.
   - Keep it under 1024 characters and avoid angle brackets.
4. Keep `SKILL.md` as the route map. Move detail into `references/` when it is long, domain-specific, or rarely needed.
5. Add scripts only when they remove repeated code generation, make validation deterministic, or handle fragile file operations.
6. Add `agents/openai.yaml` when the environment supports it. Keep UI metadata aligned with the actual skill.
7. Validate and forward-test before calling the skill production-ready.

## Review Workflow

For reviews, read the skill directory first: `SKILL.md`, metadata files, scripts, references, assets list, and any tests/evals. Then run:

```bash
python3 scripts/audit_skill.py <path-to-skill>
```

Use [references/review-rubric.md](references/review-rubric.md) for severity and findings. Lead with bugs and production risks, not praise. Give file/line references where possible.

## Evaluation Workflow

Use [references/eval-workflow.md](references/eval-workflow.md) when the skill is important, ambiguous, or user-facing enough that static review is not enough.

Minimum viable evaluation:

1. Pick 2-3 realistic prompts, including one edge case and one near miss.
2. Run with the skill and compare against no skill or the previous version.
3. Record output quality, missing steps, unnecessary work, token/time if available, and whether the description triggered appropriately.
4. Revise the skill based on generalizable failures, not overfit examples.

## Domain-Specific Guardrails

When creating SDK/API skills, require current source material such as package name, official docs URL, repo, or local implementation. For Azure SDK or Microsoft Foundry skills, follow Microsoft-style constraints: fresh docs first, explicit auth/lifecycle guidance, language-specific client setup, and test scenarios.

For generic productivity or coding skills, favor the Matt Pocock constraint: shorter `SKILL.md`, concrete examples, one-level references, and clear review checklist.

For critical production skills, borrow the Anthropic pattern: baseline comparison, user-visible review artifacts, objective assertions where possible, and trigger-description tests for should-trigger and should-not-trigger prompts.

## Completion Criteria

Before finishing, report:

- Skill path and name.
- What files changed.
- Validation commands run and results.
- Forward tests run, or why they were skipped.
- Any remaining risks or recommended follow-up.
