# Repository Instructions

## Scope

This file applies to the entire repository. A more deeply nested `AGENTS.md` adds instructions for its own directory and takes precedence where rules conflict. Do not rewrite unrelated instruction files when changing one skill.

## Repository Structure

- `skills/<skill-name>/SKILL.md` is the required entry point for each skill.
- A skill may also contain `agents/`, `assets/`, `evals/`, `examples/`, `references/`, `scripts/`, `templates/`, or `tests/`. Add supporting files only when the skill needs them.
- `README.md` and `README.zh-CN.md` are the English and Chinese repository indexes. Keep their skill lists and repository facts aligned.
- `SKILLS-GUID.md` is the agent-facing routing guide for choosing among this repository's skills. Keep it concise and do not duplicate complete skill workflows.
- `skills/Makefile` packages one skill at a time and writes archives under `skills/dist/`.

## Before Editing

1. Read the target skill's complete `SKILL.md` before changing it.
2. Follow only the references directly required by the task; resolve relative paths from the skill directory.
3. Check for a nested `AGENTS.md` in the target directory before editing.
4. Inspect `git status --short` and preserve unrelated or pre-existing changes.
5. Treat each skill as an independent package. Do not assume that commands, dependencies, or conventions from one skill apply to another.

## Skill Authoring Rules

- Keep every skill self-contained under `skills/<skill-name>/`.
- Use a lowercase hyphen-case directory name and make it match the `name` field in `SKILL.md` frontmatter.
- Give `SKILL.md` a concrete, trigger-oriented `description`; do not leave unfinished placeholder markers.
- Keep the main workflow concise. Move detailed guidance to `references/` and reusable operations to `scripts/` when that improves progressive disclosure.
- Reference bundled scripts and reference documents from `SKILL.md` so agents can discover when to use them.
- Do not add secrets, credentials, private machine paths, generated caches, dependency directories, or build output.
- When adding, removing, or renaming a skill, update both root README files and `SKILLS-GUID.md` in the same change. Update `SKILLS-GUID.md` when a skill's trigger conditions or boundaries change materially.

## Validation

Run commands from the repository root unless another directory is specified.

- For a changed skill, run the checks documented by that skill and the tests located in its own `tests/` directory. Do not claim that a repository-wide test suite exists.
- Audit a skill directory with:

  ```bash
  python3 skills/skill-engineer/scripts/audit_skill.py skills/<skill-name>
  ```

- Audit an `AGENTS.md` file with:

  ```bash
  python3 skills/agents-md-expert/scripts/audit_agents_md.py <path-to-AGENTS.md>
  ```

- Standard-library Python tests can be run for a specific skill with:

  ```bash
  python3 -m unittest discover -s skills/<skill-name>/tests
  ```

  Run this only when that directory exists and its tests use `unittest`.

- To inspect the files that would be packaged, run from `skills/`:

  ```bash
  make list <skill-name>
  ```

- Run `make package <skill-name>` from `skills/` only when packaging is requested. It creates or replaces `skills/dist/<skill-name>.zip`; verify the resulting archive with `make verify <skill-name>`.
- Do not install dependencies, run generators, or execute checks that require external services without first confirming that the task authorizes those side effects.

## Change Boundaries

- Do not edit generated artifacts directly when their source files and generator are present; update the source and regenerate with the documented command.
- Do not weaken or delete tests to make validation pass.
- Do not modify Git history, discard user changes, or push to a remote repository.
- Report missing dependencies, unavailable tools, and commands that could not be run instead of inventing substitute results.

## Instruction Maintenance

When project structure, the technology stack, build or test commands, generation workflows, or development constraints change, update the applicable `AGENTS.md` in the same change. Update only the instruction files whose scope is affected.

## Completion Report

State what changed, which checks actually ran, their results, and any unverified assumptions or remaining risks. Before finishing, confirm that the change did not leave stale entries in either root README or `SKILLS-GUID.md`, and whether an `AGENTS.md` synchronization update is required.
