# Skill Review Rubric

Use this rubric when reviewing or improving an existing skill.

## Severity

- **High**: likely to prevent correct triggering, produce unsafe or wrong outputs, rely on unavailable tools, leak private information, or fail basic validation.
- **Medium**: likely to waste substantial context, confuse execution, overfit to examples, omit important edge cases, or make future maintenance difficult.
- **Low**: style, naming, organization, or clarity issues that do not block production use.

## Review Checklist

### Frontmatter

- `name` is lowercase hyphen-case and matches the folder name.
- `description` explains capability and trigger contexts.
- Trigger information is in `description`, not only in body text.
- Description is neither too broad nor too narrow.
- Description is under 1024 characters and has no angle brackets.

### Body

- `SKILL.md` is a route map, not a full manual.
- Instructions are imperative and actionable.
- The skill explains why fragile steps matter.
- It avoids time-sensitive facts unless it tells the agent to verify them.
- It avoids private local paths, secrets, or organization-only assumptions unless the skill is explicitly private.

### Resources

- `references/` contains detailed material that should be loaded only when needed.
- Reference files are directly linked from `SKILL.md`.
- `scripts/` contains deterministic repeated operations, not throwaway examples.
- Scripts have clear arguments, useful errors, and have been run at least once.
- `assets/` contains output resources, templates, images, or boilerplate that should not be loaded into context.

### Production Behavior

- A new agent can use the skill without hidden conversation context.
- The package does not name, invoke, link to, or depend on sibling skills; cross-skill routing exists only in central repository indexes.
- Markdown links and symlinks stay inside the package unless they target public external documentation.
- The skill does not depend on a tool, MCP, package, or environment variable unless documented.
- 强依赖外部 CLI 的 Skill 设置 `external-cli: true`，用 `cli-compatibility` 指向包内契约，记录本机验证版本或明确说明不可用，探测必需能力，并定义版本不一致时的行为。
- Domain-specific skills cite or request current source material.
- Important claims are tested on realistic prompts.
- The skill includes enough negative guidance to avoid over-triggering.

## Review Output Format

Start with findings, ordered by severity:

```text
High: <issue title>
Path: <file>:<line>
Why it matters: <production impact>
Fix: <specific change>
```

Then include:

- Open questions or assumptions.
- Validation performed.
- Short change summary if edits were made.
