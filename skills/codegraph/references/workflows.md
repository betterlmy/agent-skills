# CodeGraph 跨平台工作流

## 定位 wrapper

从已加载的 `SKILL.md` 路径解析 Skill 目录，不要从被分析项目猜测相对路径。

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

## 安装 CLI

先运行 `cg check`。找不到 CLI 时，说明安装位置和副作用并让用户选择。不要未经确认执行安装命令。

检查当前 CLI 是否支持推荐入口：

```text
cg raw explore --help
cg raw node --help
```

缺少命令时可先使用 `query`、`callers`、`callees` 和 `impact`；升级仍需用户确认。

有 Node.js 的环境可选择：

```text
npm i -g @colbymchenry/codegraph@1.6.0
```

`1.6.0` 是本 Skill 当前记录的本机验证版本，不代表未经测试即可推广为最低或最高兼容版本。用户选择其他版本时，按 `cli-compatibility.md` 重新探测关键能力。

无 Node.js 时，从 [CodeGraph 官方 README](https://github.com/colbymchenry/codegraph/blob/main/README.md) 获取当前 standalone installer。不要复制未经核对的第三方安装脚本；执行远程脚本前再次确认来源和用户授权。安装完成后可能需要重新打开终端才能刷新 PATH。

## 初始化与 Git 保护

`init` 会创建本地索引目录。Git 项目必须先确认索引被忽略：

```text
git check-ignore -q --no-index -- .codegraph/.ignore-check
```

如果未忽略，编辑适用作用域的 `.gitignore`：

```gitignore
.codegraph/
```

需要覆盖嵌套项目时使用：

```gitignore
**/.codegraph/
```

随后执行：

```text
cg init .
cg status .
```

wrapper 会在 Git 项目中重复检查忽略规则；非 Git 项目不要求 `.gitignore`。

### 解读索引状态

`status` 同时报告两个互相独立的维度：

- `pendingChanges` 比较当前工作区和已有索引；全为 0 表示没有等待增量同步的文件。
- `index.builtWithVersion` 记录最近一次完整建索引所用的 CLI 版本；`index.builtWithExtractionVersion` 记录提取器版本。后者为 `null` 表示索引创建于提取器版本戳机制之前。
- `index.reindexRecommended` 表示当前提取器能生成旧索引没有的数据。它可以在 `pendingChanges` 为 0 时保持为 `true`，两者并不矛盾。

`cg sync .` 只吸收文件增删改。需要刷新提取器生成的节点、边或构建版本戳时，在用户同意后运行：

```text
cg index . --force
cg status .
```

重建后仍缺少预期关系时，再把问题归类为语法覆盖、框架识别或静态分析限制。

## 任务上下文构建与语义探索

CodeGraph 1.6.0 提供了针对研发任务的上下文构建命令 `context`，配合 `explore` 形成两级探索体系：

### 1. 任务级上下文（低 Token 推荐）：`context`

针对具体任务或流程，优先构建结构化上下文拓扑，不包含源码正文：

```text
cg context . "实现 hybrid search 逻辑" --no-code
cg context . "用户鉴权流程" --no-code -f json -n 15
```

- `--no-code`：仅输出入口点（Entry Points）、关联符号（Related Symbols）和执行路径（Call paths），将上下文消耗控制在几百 Token。
- **动态派发标记解读**：Call paths 中带有 `[event @path:line]` 或 `[callback @path:line]` 标记的调用跳跃，代表 CodeGraph 识别到的动态分发或事件注册桥接（Dynamic Dispatch Bridged），表明调用经由该文件行注册的分发器触发。

### 2. 带源码切片的探索：`explore`

不清楚具体实现位置且需要直接阅读跨文件关联源码时使用：

```text
cg explore . "认证请求如何到达数据库？" --max-files 3
cg explore . "TargetSymbol 的调用路径和潜在影响" --max-files 5
```

### 3. Token 预算与分层查询

`explore` 会逐行展开匹配文件的源码，初探复杂问题容易输出数千 Token：

1. **粗筛与拓扑**：优先使用 `cg context . "task" --no-code`，或加 `--max-files 3`，或先用 `cg node . TargetSymbol --symbols-only` 只读成员轮廓。
2. **定点细读**：通过大纲确定目标行号后，用 `cg node . --file path/to/file.ext --offset 1 --limit 100` 切片读取。
3. **定向关系**：若任务只要求理清调用方向或寻找被影响测试，直接使用 `callers`、`callees`、`impact`，避免一次性倾泻无关源码。

## 结构化查询

```text
cg files . --format tree --max-depth 2 --no-json
cg query . TargetSymbol --kind function --limit 10
cg callers . TargetSymbol --limit 20
cg callees . TargetSymbol --limit 20
cg impact . TargetSymbol --depth 2
```

调用图用于缩小范围。判断业务行为时继续读取返回的源码和相关测试，特别关注动态注册、反射、生成代码和跨进程调用。

框架路由、HTTP 和数据语义需要分别判断：

- 框架路由边是尽力而为；先排除旧索引、未覆盖文件和当前语法形式没有被识别。
- 前端请求和后端路由即使使用相同 URL，也可能只是两个字符串，不保证形成跨语言图边。
- ORM 字段赋值、数据库状态转换和通知事件之间的业务关联通常不是调用边，应继续检索字段、状态值、事件名、迁移和测试。

## 动态语言特性与路由定位范式

静态 AST 索引无法捕获全部动态特性，遇下列情况时采用标准组合策略：

### 1. Go 隐式接口实现定位
Go interface 没有 `implements` 关键字，接口节点与实现 struct 之间没有直接显式调用边：
1. `cg node . InterfaceName` 获取接口定义及核心方法名列表（如 `Complete(ctx, ...)`）。
2. `cg query . Complete --kind method` 检索所有挂载了该同名方法的 struct 或文件。
3. 结合具体签名与入参结构体，迅速锁定实际实现类。

### 2. Web 框架动态路由反查
在 Gin、Echo 等框架中，`r.POST("/path", Handler)` 是将 Handler 作为函数值参数传入，其 `callers` 经常为空：
1. 若反查 Handler 无 callers，不要误判为死代码。
2. 执行 `cg query . "/path"` 检索是否存在显式路由节点。
3. 若无显式节点，探索或阅读路由汇总方法（如 `cg node . Routes` 或 `cg explore . "路由注册"`）。

### 3. 拓扑关系呈现
需要向用户展示调用链路或架构影响面时，直接基于 `impact` 或 `callers` 输出标准 `mermaid` 流程图代码块（如 `flowchart LR`），保持零外部工具依赖。

## 选择回归测试

```text
cg affected . path/to/changed_file.ext
git diff --name-only | cg affected . --stdin
cg affected . path/to/changed_file.ext --filter "**/*_test.*"
```

`affectedTests` 为空时检查：

- 项目是否存在可索引测试文件。
- 测试命名和 `--filter` 是否匹配。
- 索引是否覆盖变更文件和测试文件。
- 变更是否属于配置、文档、生成文件或不支持的语言。

## 维护与清理

当前版本会自动同步常规文件变化。在执行了代码写入或重构后，若后续任务需要继续依赖图查询验证，建议执行一次：

```text
cg sync .
```

仅在状态异常、提取器版本更新或显式要求完整重建时使用：

```text
cg sync .
cg index . --force
cg unlock .
```

升级或删除索引前先确认：

```text
cg upgrade --check
cg upgrade
cg uninit . --force
```

`upgrade` 会优先使用 CLI 原生命令。旧版 CLI 没有原生升级能力时，wrapper 仅在存在 npm 的环境中提供 fallback；否则要求按官方方式重新安装。

## 检索范式差异：传统 Agent 检索 vs CodeGraph 语义图谱

Agent 在进行代码库检索时，必须理解**基于正则/文本的平面匹配**与**基于 AST/符号引用的知识图谱**的根本区别，从而在不同任务阶段选用最适工具：

### 1. 传统检索（`rg` / `grep` / `find` / `read`）的优缺点
- **核心机制**：逐行扫描文件内容，基于字符子串或正则表达式进行模式匹配。
- **不可替代的优势**：
  - **零前期成本**：不需要建索引，任何临时文件、大型仓库即搜即用。
  - **全覆盖非代码资产**：配置文件（YAML、JSON、TOML、INI）、SQL 脚本、环境变量、Dockerfile、CI 脚本、Markdown 文档、注释与日志模板。
  - **精确字面量命中**：搜寻确切的错误信息（如 `"token_budget exceeded"`）、固定路由前缀、特定常量值。
- **在代码语义层面的致命局限**：
  - **无视符号身份**：搜一个符号名，定义、调用、导入声明、文档注释全混在一起，无法快速定位真正的签名与定义点。
  - **同名符号噪音泛滥**：常见方法名（如 `Search`、`Close`、`Handler`、`Validate`）会在大项目中触发数百个无关命中，极难筛选出目标类的实现。
  - **调用链（Call Graph）追踪断层**：跨文件多层调用（A -> B -> C）无法一次性追踪，Agent 必须人肉逐层执行 grep 并肉眼拼接，极易漏看分支或产生幻觉。
  - **测试依赖盲猜**：当修改了一个公共底层函数时，传统方式只能按文件名猜测（如搜同目录下的 `*_test.go`），无法识别跨模块甚至跨目录的端到端测试与集成测试。

### 2. CodeGraph 语义图谱的核心突破
- **核心机制**：多语言语法解析器构建抽象语法树（AST），提取符号表，解析跨文件/跨作用域的引用关系，并在嵌入式数据库中维护有向调用图。
- **核心优势**：
  - **符号与作用域消歧**：直接提取结构体、接口、方法、函数等实体，清晰展示方法所属的接收者（Receiver/Class），消除同名方法的噪音。
  - **原生图拓扑追溯**：
    - 向上追溯：`cg callers` 明确列出调用此符号的直接函数。
    - 向下展开：`cg callees` 明确列出此符号内部调用的依赖。
    - 深度波及：`cg impact` 递归分析深度调用链。
  - **自动化测试回归识别**：`cg affected` 沿着真实的依赖图向上追溯引用链路，自动找出依赖被修改文件的所有测试用例（`affectedTests`），彻底解决漏测问题。
  - **端到端流程穿透**：`cg explore` 一次性整合自然语言流程中的关联符号、关键调用路径与代码切片。
- **边界与局限**：
  - 动态拼接的 URL、反射动态调用、ORM 内部字符串 SQL 无法形成静态图边，仍需搭配 `rg` 与源码核验。

### 3. 场景决策规则

- **精确文本与配置查找**（错误日志、常量值、配置项、SQL 语句、环境变量、代码注释）：使用 `rg` / `grep`。文本匹配无语法解析开销，且 100% 覆盖非代码文件。
- **任务级上下文与端到端调用流**：使用 `cg context <project> "<task>" --no-code`。低 Token 一次性获取入口、关联符号及调用路径。
- **符号定义与结构大纲**（类/结构体成员、方法签名、定义位置）：使用 `cg node <project> <symbol> --symbols-only` 或 `cg query`。结构化消歧，不受同名注释或字面量污染。
- **跨文件调用关系追溯**（反查上游调用方或展开下游依赖）：使用 `cg callers`（查 callers）/ `cg callees`（查 callees）。直接获取确凿图拓扑，避免人工逐层 grep 拼接。
- **改动波及面评估与回归测试筛选**：使用 `cg impact`（查波及符号）/ `cg affected`（查受影响测试文件）。基于真实依赖拓扑，避免漏测。
- **具体源码实现精读**：使用 `cg explore`（跨文件切片）或 `read`（最终确认当前磁盘确凿代码）。

## 降级策略

- 精确字符串、错误消息、环境变量：使用 `rg` 或宿主等价能力。
- wrapper 无法运行：用相同参数直接调用 `codegraph` CLI。
- 索引为空或语言不支持：使用文件列表、文本搜索和直接阅读。
- CodeGraph 与源码不一致：检查状态和 staleness 提示，必要时 `sync`；最终以源码和测试为准。

## 效果评估

比较 CodeGraph 与常规检索时，为两条路径使用同一组问题：

1. 定位一个已知符号及源码。
2. 追踪直接调用方、被调用方或端到端流程。
3. 评估公共符号或变更文件的影响面和受影响测试。

记录定位步骤、定义与引用区分、调用路径、遗漏、索引副作用和最终源码验证。不要只根据主观感受宣称更快或更准确。
