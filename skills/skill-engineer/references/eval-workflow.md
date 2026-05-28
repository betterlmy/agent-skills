# Skill Evaluation Workflow

Use this when static review is not enough to know whether a skill works.

## Choose Evaluation Depth

- **Lightweight**: 2-3 prompts, manual comparison. Use for normal private skills.
- **Baseline comparison**: run with-skill and without-skill or old-skill outputs. Use for production or shared skills.
- **Trigger evaluation**: include should-trigger and should-not-trigger prompts. Use when the main risk is under-triggering or over-triggering.
- **Full benchmark**: assertions, timing, token counts, and user review artifacts. Use for high-value skills or public distribution.

## Prompt Set

Create realistic prompts:

- One common happy path.
- One edge case with missing, ambiguous, or messy inputs.
- One near miss that should not trigger the skill or should route to another skill.
- For domain skills, include a prompt that requires current source material.

Avoid toy prompts such as "make a PDF" or "write a skill". They do not test whether the skill guides hard decisions.

## Baselines

- New skill: compare against no skill.
- Existing skill: snapshot the old version before edits and compare against it.
- Major rewrite: compare old, new, and no-skill if time allows.

## What to Record

For each run, capture:

- Prompt.
- Skill version or baseline label.
- Output files or final answer.
- Whether the expected workflow was followed.
- Missing or unnecessary steps.
- Objective assertions if available.
- Time and token usage if the runtime reports them.
- User feedback if review is subjective.

## Trigger Checks

Create 8-20 queries when trigger quality matters:

- Should-trigger queries: varied phrasings, casual wording, real file names, adjacent tasks that still require this skill.
- Should-not-trigger queries: near misses, shared keywords with different intent, tasks better handled by another skill.

Improve `description` based on failures. Do not broaden it until every keyword triggers; broad descriptions cause the wrong skill to load.

## Iteration Rule

Only revise based on failures that generalize. Do not hard-code one eval prompt into the skill. If the same helper code appears in multiple eval runs, move it into `scripts/`. If agents repeatedly search for the same domain facts, move stable facts into `references/` and require live verification for unstable facts.

