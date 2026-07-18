---
name: codegraph
description: 使用 CodeGraph CLI 做本地代码库索引、符号检索、调用关系分析和改动影响分析。Use when需要通过 Bash 命令行探索代码实现位置、查看文件结构、查询 callers/callees、评估 refactor 影响或定位受影响测试，且项目可使用 codegraph CLI。
allowed-tools: Bash(bash:*) Bash(codegraph:*) Bash(command:*) Bash(chmod:*) Bash(test:*) Bash(npm:*) Bash(curl:*)
---

# CodeGraph

## 默认行为

所有命令优先通过本 skill 自带 wrapper 执行。执行前先把脚本路径按 skill 目录解析：

```bash
bash scripts/codegraph.sh check
```

如果 `check` 提示找不到 `codegraph`，先安装 CLI：

```bash
npm i -g @colbymchenry/codegraph
```

也可以使用官方无 Node 安装脚本：

```bash
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
```

如果安装在非 PATH 位置，用 `CODEGRAPH_BIN` 指定可执行文件：

```bash
CODEGRAPH_BIN=/path/to/codegraph bash scripts/codegraph.sh check
```

如果项目没有 `.codegraph/`，先初始化索引。`init` 会在项目内写入 `.codegraph/` 索引目录：

```bash
bash scripts/codegraph.sh init .
```

只读评估或临时分析结束后，如果不希望留下索引状态，运行清理命令并用 `git status --short` 确认工作树：

```bash
bash scripts/codegraph.sh uninit . --force
```

官方文档中的 `codegraph init -i` / `--index` 也可以传给 wrapper；当前 CLI 版本中 `init` 已默认索引，`-i` 仍作为兼容参数接受。初始化后用 `status` 确认 `initialized`、`fileCount` 和 `nodeCount`；如果索引为空，再运行 `index`。

日常使用优先顺序：

1. 确认索引状态：`status`
2. 初次进入项目：`files --format tree --max-depth 2 --no-json`
3. 不清楚实现位置：`query`
4. 追调用链：`callers` 或 `callees`
5. 改动前评估影响：`impact`
6. 选择回归测试：`affected`；如果结果为空，先确认项目内是否存在可索引测试文件
7. 索引疑似过期：`sync`，必要时 `index --force`
8. 确认不再需要项目索引：`uninit --force`

## 核心命令

```bash
bash scripts/codegraph.sh status .
bash scripts/codegraph.sh files . --format tree --max-depth 2 --no-json
bash scripts/codegraph.sh query . TargetSymbol --limit 5
bash scripts/codegraph.sh files . --format flat --max-depth 2
bash scripts/codegraph.sh callers . TargetSymbol --limit 20
bash scripts/codegraph.sh callees . TargetSymbol --limit 20
bash scripts/codegraph.sh impact . TargetSymbol --depth 2
bash scripts/codegraph.sh affected . path/to/changed_file.ext
bash scripts/codegraph.sh uninit . --force
```

wrapper 对查询类命令默认加 `--json`，便于解析和引用。需要人类可读输出时加 `--no-json`：

```bash
bash scripts/codegraph.sh query . TargetSymbol --limit 5 --no-json
```

## 索引维护

```bash
bash scripts/codegraph.sh init .
bash scripts/codegraph.sh sync .
bash scripts/codegraph.sh index . --force
bash scripts/codegraph.sh unlock .
bash scripts/codegraph.sh upgrade --check
```

`sync` 适合普通增量变更；如果查询结果明显不准、文件大量移动、语言解析结果异常，再用 `index --force`。

`upgrade` 会优先调用 CLI 原生命令；如果当前安装版本还不支持，则由 wrapper 使用 npm 查询或安装 `@colbymchenry/codegraph`。

## 使用边界

- CodeGraph 适合符号、文件结构、调用关系和影响分析；精确文本、错误消息、配置项仍优先用 `rg`。
- 查询输出只说明索引视角，不等同于完整语义证明；涉及行为判断时还要读取相关源码和测试。
- 调用图和影响面不能覆盖所有运行时行为；外部依赖、生成代码、动态注册、反射、初始化副作用等需要补充源码或常规检索确认。
- `affected` 结果为空不等于没有回归风险；先检查测试文件是否存在、命名是否符合规则、过滤条件是否过窄、索引是否覆盖目标文件。
- 对大型仓库，先用 `files --max-depth` 缩小范围，再做 `query` 或调用图分析。
- 如果 CLI 不存在、索引损坏或语言不支持，直接退回 `rg`、`rg --files` 和常规文件阅读。

更多场景见 [references/workflows.md](references/workflows.md)。需要理解 CodeGraph 架构背景、索引模型或工具设计取舍时，再读取 [references/knowledge.md](references/knowledge.md)。
