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
npm i -g @colbymchenry/codegraph@1.4.1
```

`1.4.1` 是本 Skill 当前记录的本机验证版本，不代表未经测试即可推广为最低或最高兼容版本。用户选择其他版本时，按 `cli-compatibility.md` 重新探测关键能力。

无 Node.js 时，从 [CodeGraph 官方 README](https://github.com/colbymchenry/codegraph/blob/main/README.md) 获取当前 standalone installer。不要复制未经核对的第三方安装脚本；执行远程脚本前再次确认来源和用户授权。安装完成后可能需要重新打开终端才能刷新 PATH。

## 初始化与 Git 保护

`init` 会创建本地索引目录。Git 项目必须先确认索引被忽略：

```text
git check-ignore -q --no-index -- .codegraph/.ignore-check
```

如果未忽略，取得用户同意后编辑适用作用域的 `.gitignore`：

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

## 语义探索与源码读取

不清楚实现位置或需要理解完整流程时，优先使用 `explore`：

```text
cg explore . "认证请求如何到达数据库？"
cg explore . "TargetSymbol 的调用路径和潜在影响" --max-files 12
```

读取单个符号或文件：

```text
cg node . TargetSymbol
cg node . TargetSymbol --file path/to/file.ext
cg node . --file path/to/file.ext --offset 1 --limit 200
cg node . --file path/to/file.ext --symbols-only
```

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

当前版本会自动同步常规文件变化。仅在状态异常时使用：

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
