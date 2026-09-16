---
metadata:
  external-cli: "true"
  cli-compatibility: "references/cli-compatibility.md"
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

先阅读 [CLI 兼容性契约](references/cli-compatibility.md)，再检查当前版本和关键能力：

```text
cg check
```

如果找不到 CLI，先说明安装会修改用户环境，并让用户选择官方 standalone installer 或 npm 全局安装；未经明确同意不要安装、升级或执行远程脚本。安装方式和平台说明见 [工作流参考](references/workflows.md)。

首次使用 `context`、`explore` 或 `node` 时，可用 `cg raw context --help`、`cg raw explore --help` 和 `cg raw node --help` 做能力检查。旧版 CLI 不支持时，先使用结构化查询降级；只有用户同意后才升级。

首次在项目中初始化前：

1. 确认目标项目和索引写入范围。
2. 如果是 Git 项目，使用 `git check-ignore` 确认 `.codegraph/` 已被忽略。
3. 未忽略时，在适用作用域的 `.gitignore` 中加入 `.codegraph/`；需要覆盖嵌套项目时加入 `**/.codegraph/`。这项修改是 Git 项目初始化索引的前置处理。
4. 运行 `cg init .`；wrapper 会拒绝在未忽略索引目录的 Git 项目中初始化。
5. 用 `cg status .` 确认索引状态。

不要因为分析结束就自动删除索引。只有用户明确要求清理时才运行 `cg uninit . --force`，随后检查工作区状态。

## 工具选型：传统文本检索 vs CodeGraph 语义图谱

Agent 在代码理解时应严格区分**文本字面量检索**与**AST 语义图谱分析**，避免工具误用：

| 任务场景 | 首选工具 | 决策依据与典型用例 |
| --- | --- | --- |
| **精确字面量 / 配置查找** | `rg` / `grep` | 查找精确错误日志、常量值、环境变量、URL 路径字面量、SQL 表与字段、YAML/JSON 配置。文本检索速度快且无视语法规则，不受语言 AST 提取器覆盖限制。 |
| **符号定义与结构大纲** | `cg query` / `cg node` | 查找结构体、类、接口的成员签名与定义位置。天然隔离同名符号干扰，不被注释、文档或字符串字面量污染。 |
| **跨文件调用追踪** | `cg callers` / `cg callees` | 向上反查“谁调用了此函数”或向下展开“它调用了哪些依赖”。替代传统 `rg` 繁琐的人肉反复查找与多层手工拼接。 |
| **端到端业务流与任务上下文** | `cg context` / `cg explore` | “某个请求/流程从入口到存储经历了什么”；优先使用 `cg context --no-code` 极速获取入口、关联符号与调用路径流（极省 Token）；需要关联源码切片时使用 `cg explore --max-files 3`。 |
| **改动影响面与回归测试** | `cg impact` / `cg affected` | 评估重构某个函数波及的调用链；直接根据依赖图反查受影响的测试文件（`affectedTests`），无需按文件名硬猜。 |
| **最终代码精读与确认** | `read` | 确认最终业务细节与改动边界。在 CodeGraph 缩小范围后，以实际磁盘源码为准。 |

## 默认检索顺序

1. `cg status .`：确认项目是否已初始化。
2. `cg context . "任务目标或问题" --no-code`：任务级上下文推荐首选入口，低 Token 一次性获取入口点（Entry Points）、关联符号（Related Symbols）与调用链路（Call paths）。
3. `cg explore . "问题、流程或目标符号" --max-files 3`：需要同时获取关联源码切片与调用路径时的探索入口。
4. `cg node . TargetSymbol`：读取单个符号及其调用关系；加 `--symbols-only` 仅读取成员轮廓。
5. `cg node . --file path/to/file --offset 1 --limit 200`：按行读取文件切片并查看依赖。
6. 需要结构化细查时再使用 `files`、`query`、`callers`、`callees`、`impact` 和 `affected`。

```text
cg files . --format tree --max-depth 2 --no-json
cg query . TargetSymbol --limit 5
cg callers . TargetSymbol --limit 20
cg callees . TargetSymbol --limit 20
cg impact . TargetSymbol --depth 2
cg affected . path/to/changed_file.ext
```

`status`、`files`、`query`、`callers`、`callees`、`impact` 和 `affected` 默认输出 JSON；需要原始可读输出时加 `--no-json`。`explore` 和 `node` 使用 CLI 原生文本输出。

### Token 预算与探索分层

- **任务初探优先使用 `cg context . "task" --no-code`**：只输出关键入口、相关符号及调用流拓扑，完全不展开源码正文，将单次探索消耗压缩在几百 Token 内。
- `cg explore` 会展开匹配文件的完整源码。在需要阅读源码时，优先加 `--max-files 3` 控制篇幅；或先用 `cg query` 定位核心符号后使用 `cg node --symbols-only` 读取大纲，避免无谓消耗上下文。
- 仅需要调用关系或影响面时，优先使用 `cg callers`、`cg callees` 或 `cg impact`，不要用未加文件限制的 `explore` 代替精确定位。

## 索引维护

当前 CodeGraph 初始化后会自动同步文件变化。代码写入或重构后，若后续任务继续依赖 CodeGraph 检查调用关系或受影响测试，先执行 `cg sync .` 吸收工作区变更，避免索引滞后。

只有状态异常、文件大量移动或结果明显过期时才手工执行：

```text
cg sync .
cg index . --force
cg unlock .
```

解读 `status` 时区分增量同步与提取器版本：

- `pendingChanges` 为 0 只表示工作区没有等待增量同步的文件，不表示索引由当前提取器完整构建。
- `index.builtWithExtractionVersion` 为 `null` 或低于 `currentExtractionVersion` 时，当前 CLI 会设置 `reindexRecommended: true`；`builtWithVersion` 只记录完整建索引时的 CLI 版本。
- `sync` 只处理文件增删改，不能替代完整重建。出现上述组合时，先说明原因，直接运行 `cg index . --force`，再用 `cg status .` 复核。

升级会修改全局或 standalone 安装。只有用户明确要求时才运行 `cg upgrade --check` 或 `cg upgrade`。

## 使用边界

- 精确字符串、错误消息、配置项、环境变量和非代码文件优先用 `rg` 或宿主等价工具。
- CodeGraph 结果是索引视角；运行时注册、反射、生成代码、外部依赖和初始化副作用仍需源码与测试确认。
- **Go 隐式接口实现定位**：`node` 只展示接口定义与显式调用。反查接口实现类时，先读取接口核心方法名，再用 `cg query . MethodName --kind method` 检索拥有该方法的结构体。
- **Web 框架动态路由溯源**：路由处理函数（Handler）若直接作为函数值传给框架引擎（如 Gin/Echo/Fiber），其 `callers` 可能为空。此时优先通过 `cg query . "/api-path"` 反查路由节点，或阅读框架路由注册函数（如 `Routes()`）。
- **依赖拓扑自包含可视化**：向用户展示调用链路或架构影响面时，可将 `cg impact` 或 `cg callers` 的输出直接组织为 Markdown 内嵌的标准 `mermaid` 流程图块（如 `flowchart LR`），保持零外部工具依赖。
- 框架路由识别是尽力而为。受支持框架的路由缺失且状态建议重建时，先完整重建再复测，不要直接归因于静态分析能力。
- HTTP 路径字符串、动态 URL 拼接、前后端跨语言消费者、ORM 字段和业务状态关系不保证形成图边；结合 `rg`、源码、迁移和测试补齐影响面。
- `affected` 为空不等于没有回归风险；检查测试命名、过滤条件、语言支持和索引覆盖。
- CLI 不存在、语言不支持、索引损坏或 wrapper 不兼容时，退回常规文件检索，不要阻塞任务。
- 安装、升级和 `uninit` 都会改变用户环境或清理索引，执行前遵循用户授权边界；Git 项目初始化时为忽略 `.codegraph/` 而进行的 `.gitignore` 编辑除外。

更多安装、跨平台命令、降级和评估场景见 [工作流参考](references/workflows.md)；版本漂移和能力探测见 [CLI 兼容性契约](references/cli-compatibility.md)。

本 Skill 及其分发包使用 [MIT License](LICENSE)。
