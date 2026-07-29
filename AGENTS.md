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

### Skill 独立性设计原则

- 每个 `skills/<skill-name>/` 都必须是可单独安装、读取、执行和验证的独立分发包；假设其他 sibling skill 均未安装。
- 一个 skill 的 `SKILL.md`、metadata、references、scripts、assets、examples、evals 和 tests 不得点名、调用、组合、链接或依赖其他 sibling skill，也不得读取 `../<other-skill>/` 下的文件。
- 不要在 skill 包内写“改用某个 skill”“组合某个 skill”或“先运行某个 skill”等路由说明。跨 skill 的选择、互补关系和组合流程只能写在仓库根 `README.md`、`README.zh-CN.md` 或 `SKILLS-GUID.md` 等中央索引中。
- 能力边界必须用任务类型描述，例如“本 Skill 不用于仅审查单次 PR/diff”，不要用其他 skill 名称描述边界。
- 如果工作流依赖外部 CLI、MCP、SDK、运行时或服务，当前 skill 必须自行说明前置条件、授权边界、调用方式、失败降级和验证方法；外部工具与 sibling skill 同名时，也不得把对应 sibling skill 当作前置条件。
- 当前 skill 所需的私有模板、脚本和参考资料必须放入自身目录并从 `SKILL.md` 可发现；不得用跨包相对路径、指向包外的符号链接或用户机器上的另一个 skill 安装路径复用资源。
- 审查或修改 skill 时，必须运行独立性检查；发现 sibling 名称引用、越出包目录的本地 Markdown 链接或包外符号链接时视为失败，不得以“组合使用更方便”为理由保留。

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
