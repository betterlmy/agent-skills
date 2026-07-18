---
name: codegraph
description: 使用 CodeGraph CLI 在本地代码库中进行语义探索、符号检索、源码读取、调用关系和改动影响分析。Use when 需要理解代码结构、追踪 callers/callees、评估重构影响或定位受影响测试；适用于 Windows、macOS 和 Linux，精确字符串与非代码文本检索不触发本 Skill。
---

# CodeGraph

## 启动方式

先把本 `SKILL.md` 所在目录的绝对路径保存为 Skill 目录。不得假设当前工作目录就是 Skill 目录，也不要直接运行相对路径 `scripts/codegraph.*`。

macOS、Linux、WSL 或 Git Bash：

```bash
CODEGRAPH_SKILL_DIR="/absolute/path/to/installed/codegraph"
cg() { bash "$CODEGRAPH_SKILL_DIR/scripts/codegraph.sh" "$@"; }
```

Windows PowerShell：

```powershell
$CodeGraphSkillDir = "C:\absolute\path\to\installed\codegraph"
function cg { & (Join-Path $CodeGraphSkillDir "scripts/codegraph.ps1") @args }
```

`cg` 只在当前 shell 会话有效。若宿主无法执行对应 wrapper，可使用相同参数直接调用 `codegraph` CLI。

## 前置检查

```text
cg check
```

如果找不到 CLI，先说明安装会修改用户环境，并让用户选择官方 standalone installer 或 npm 全局安装；未经明确同意不要安装、升级或执行远程脚本。安装方式和平台说明见 [工作流参考](references/workflows.md)。

首次使用 `explore` 或 `node` 时，可用 `cg raw explore --help` 和 `cg raw node --help` 做能力检查。旧版 CLI 不支持时，先使用结构化查询降级；只有用户同意后才升级。

首次在项目中初始化前：

1. 确认目标项目和索引写入范围。
2. 如果是 Git 项目，使用 `git check-ignore` 确认 `.codegraph/` 已被忽略。
3. 未忽略时，先取得用户同意，再在适用的 `.gitignore` 中加入 `.codegraph/` 或 `**/.codegraph/`。
4. 运行 `cg init .`；wrapper 会拒绝在未忽略索引目录的 Git 项目中初始化。
5. 用 `cg status .` 确认索引状态。

不要因为分析结束就自动删除索引。只有用户明确要求清理时才运行 `cg uninit . --force`，随后检查工作区状态。

## 默认检索顺序

1. `cg status .`：确认项目是否已初始化。
2. `cg explore . "问题、流程或目标符号"`：默认入口，一次获取相关源码、调用路径和影响摘要。
3. `cg node . TargetSymbol`：读取单个符号及其调用关系。
4. `cg node . --file path/to/file --offset 1 --limit 200`：按行读取文件并查看依赖。
5. 需要结构化细查时再使用 `files`、`query`、`callers`、`callees`、`impact` 和 `affected`。

```text
cg files . --format tree --max-depth 2 --no-json
cg query . TargetSymbol --limit 5
cg callers . TargetSymbol --limit 20
cg callees . TargetSymbol --limit 20
cg impact . TargetSymbol --depth 2
cg affected . path/to/changed_file.ext
```

`status`、`files`、`query`、`callers`、`callees`、`impact` 和 `affected` 默认输出 JSON；需要原始可读输出时加 `--no-json`。`explore` 和 `node` 使用 CLI 原生文本输出。

## 索引维护

当前 CodeGraph 初始化后会自动同步文件变化。只有状态异常、文件大量移动或结果明显过期时才手工执行：

```text
cg sync .
cg index . --force
cg unlock .
```

升级会修改全局或 standalone 安装。只有用户明确要求时才运行 `cg upgrade --check` 或 `cg upgrade`。

## 使用边界

- 精确字符串、错误消息、配置项、环境变量和非代码文件优先用 `rg` 或宿主等价工具。
- CodeGraph 结果是索引视角；运行时注册、反射、生成代码、外部依赖和初始化副作用仍需源码与测试确认。
- `affected` 为空不等于没有回归风险；检查测试命名、过滤条件、语言支持和索引覆盖。
- CLI 不存在、语言不支持、索引损坏或 wrapper 不兼容时，退回常规文件检索，不要阻塞任务。
- `init`、`.gitignore` 编辑、安装、升级和 `uninit` 都会改变状态，执行前遵循用户授权边界。

更多安装、跨平台命令、降级和评估场景见 [工作流参考](references/workflows.md)。

本 Skill 及其分发包使用 [MIT License](LICENSE)。
