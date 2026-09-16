# CLI 兼容性

<!-- cli-compatibility-contract:v1 -->

| 字段 | 值 |
| --- | --- |
| 工具 | CodeGraph CLI |
| 分发标识 | `@colbymchenry/codegraph` |
| 本机验证版本 | `1.6.0` |
| 验证日期 | `2026-09-16` |
| 版本策略 | 记录已验证版本，以能力探测决定其他版本能否继续 |

本机验证版本是可复现基线，不等同于最低或最高支持版本。不要仅凭版本号推断兼容，也不要自动升级用户环境。

## 关键能力

运行 `cg check`，确认版本可读取，且 `status`、`explore`、`context`、`node`、`affected` 的 `--help` 可用。首次依赖 JSON 状态字段时，还应在已初始化项目中检查实际输出：

```text
cg status .
```

`1.6.0` 核心能力契约：
- `explore`：支持自然语言流程与符号关联展开，支持 `--max-files`；
- `context`：1.6.0 原生任务级上下文构建，支持 `--no-code`（纯结构无源码，极省 Token）、`-f/--format markdown|json`、`-n/--max-nodes`；
- `node`：支持单符号读取与带行号文件切片，支持 `--symbols-only` 成员轮廓读取；
- `affected`：支持从源码变动反查测试，支持 `-d/--depth`（默认 5）与 `-q/--quiet`；
- `daemons`：管理后台索引监视进程。

`index.builtWithExtractionVersion`、`index.currentExtractionVersion` 和 `index.reindexRecommended` 已在 `1.6.0`（提取器版本 25）验证。字段缺失时，不得把缺失值解释为旧索引；退回文件变化、源码和测试证据，并说明当前 CLI 没有提供提取器版本判据。

## 版本不一致时

- 版本不同但关键能力存在：继续执行，并报告“版本未经本 Skill 基线验证”。
- `context`、`explore` 或 `node` 缺失：退回 `query`、`callers`、`callees`、`impact` 和源码读取。
- 状态字段缺失：不要套用基线版本的字段语义。
- 关键命令缺失或参数不兼容：停止使用对应路径，报告实际版本和失败能力；升级必须获得用户同意。

需要复现当前基线且用户已授权安装时，可使用：

```text
npm i -g @colbymchenry/codegraph@1.6.0
```
