# CodeGraph CLI 工作流

## 快速定位实现

适合用户只知道一个类型名、函数名、组件名或近似关键词时：

```bash
bash scripts/codegraph.sh status .
bash scripts/codegraph.sh query . TargetSymbol --limit 10
```

如果结果太多，增加 kind：

```bash
bash scripts/codegraph.sh query . TargetSymbol --kind struct --limit 10
```

## 浏览项目结构

先用浅层结构建立边界，再深入某个目录：

```bash
bash scripts/codegraph.sh files . --format tree --max-depth 2 --no-json
bash scripts/codegraph.sh files . --filter path/to/module --format flat
```

## 调用关系分析

查谁调用某个符号：

```bash
bash scripts/codegraph.sh callers . TargetSymbol --limit 20
```

查某个符号调用了谁：

```bash
bash scripts/codegraph.sh callees . TargetSymbol --limit 20
```

调用图结果用于缩小阅读范围；真正判断行为时，仍需要打开相关源码和测试。外部依赖、生成代码、动态注册、反射和初始化副作用不一定能被调用图完整表达。

## 改动影响评估

重构或修改公共函数前，先查影响面：

```bash
bash scripts/codegraph.sh impact . TargetSymbol --depth 2
```

depth 越大结果越宽，默认从 2 开始。影响面过大时，先按目录或模块拆小任务。

## 选择回归测试

根据已改文件查受影响测试：

```bash
bash scripts/codegraph.sh affected . path/to/changed_file.ext
```

也可以从标准输入传文件列表：

```bash
git diff --name-only | bash scripts/codegraph.sh affected . --stdin
```

如果测试命名不符合默认规则，用 `--filter` 指定：

```bash
bash scripts/codegraph.sh affected . path/to/changed_file.ext --filter '**/*_test.*'
```

如果 `affectedTests` 为空，不要直接等同于“没有测试需要跑”。先检查：

- 项目内是否存在可索引测试文件。
- 测试文件命名是否符合工具默认规则。
- `--filter` 是否过窄或路径不匹配。
- 索引状态是否覆盖了变更文件和测试文件。
- 变更是否属于配置、文档、生成文件或工具尚不支持的语言。

## 索引维护

首次初始化：

```bash
bash scripts/codegraph.sh init .
bash scripts/codegraph.sh status .
```

如果沿用官方 README 的写法，也可以显式传 `--index`：

```bash
bash scripts/codegraph.sh init . --index
```

普通增量：

```bash
bash scripts/codegraph.sh sync .
```

查询明显过期或大规模移动文件后：

```bash
bash scripts/codegraph.sh index . --force
```

遇到 stale lock：

```bash
bash scripts/codegraph.sh unlock .
```

删除当前项目索引：

```bash
bash scripts/codegraph.sh uninit . --force
```

检查 CLI 是否有新版本：

```bash
bash scripts/codegraph.sh upgrade --check
```

如果当前版本尚未实现 `upgrade` 原生命令，wrapper 会自动使用 npm fallback。也可以手动运行：

```bash
npm i -g @colbymchenry/codegraph
```

## 降级策略

- 精确字符串、错误消息、环境变量名：用 `rg`。
- 文件不存在、索引为空、语言不支持：用 `rg --files` 和直接读文件。
- CodeGraph 输出和源码不一致：先 `sync`，再复查；仍不一致时以源码为准。

## 评估 CodeGraph 效果

当用户要求比较“使用 CodeGraph”和“不使用 CodeGraph”的差异时，用同一组问题做对照，不要只给主观判断。

建议选择 2-3 个通用问题：

- 查一个已知符号的定义位置。
- 查一个符号的直接调用方和被调用方。
- 查一个公共符号或变更文件的影响面和受影响测试。

记录两条路径：

- CodeGraph 路径：`status`、必要时 `init`、`files`、`query`、`callers/callees`、`impact`、`affected`。
- 常规路径：`rg --files`、`rg`、语言工具或直接阅读文件。

对比维度：

- 定位步骤数量。
- 是否区分定义和引用。
- 是否能自动给出二级影响面。
- 是否需要补充源码确认。
- 是否遗漏外部依赖、生成代码、动态行为或测试文件。
- 是否产生索引目录等工作树副作用。

输出报告时必须说明限制：CodeGraph 是索引视角，适合缩小范围；最终行为、运行时路径和回归风险仍要结合源码、测试和常规检索确认。
