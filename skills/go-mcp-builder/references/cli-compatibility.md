# MCP 一致性测试 CLI 兼容性契约

<!-- cli-compatibility-contract:v1 -->

| 字段 | 取值 |
| --- | --- |
| 命令 | `npm exec --package=@modelcontextprotocol/conformance -- conformance` |
| 分发包 | `@modelcontextprotocol/conformance` |
| 本机验证版本 | `0.2.0-alpha.11` |
| 验证日期 | 2026-09-04 |
| 当前源码基线 | `0.2.0-alpha.11`（截至 2026-09-04） |
| 用途说明 | 作为 MCP 服务端与客户端一致性验证的辅助检查手段 |

之所以记录 Alpha 版本，是因为稳定的 `0.1.x` 系列尚未完全覆盖完整的 `2026-07-28` 规范要求集。本条目不代表对该 Alpha 版本具有通用长期稳定性的承诺。

## 关键能力

在实际运行测试套件前，先在不改动项目现有依赖的前提下进行探测：

```text
npm exec --yes --package=@modelcontextprotocol/conformance@0.2.0-alpha.11 -- conformance --version
npm exec --yes --package=@modelcontextprotocol/conformance@0.2.0-alpha.11 -- conformance list --requirements 2026-07-28
npm exec --yes --package=@modelcontextprotocol/conformance@0.2.0-alpha.11 -- conformance server --help
```

`npm exec` 命令在未安装该包时会尝试下载并连接远程 Registry。执行前必须取得当前任务的明确授权，并配置当前开发环境批准的镜像源。严禁将 npm 临时缓存、`node_modules` 依赖目录、测试产物目录或认证凭据误提交进版本库。

针对具体的业务产品服务端，仅运行与其对外声明的能力以及所采用的认证模式相匹配的测试用例。全量 SDK 要求集可能会预设特定的测试用 Tool 或标准 OAuth 行为，而采用内部 API Key 方案的实际业务产品可能刻意不暴露此类测试特性。

## 版本不一致时

- 若运行环境中安装了其他版本，但该版本同样提供了 `list --requirements`、`--spec-version` 以及服务端模式的通信报文 Schema 校验能力，在明确记录该版本超出当前基线后，允许继续使用；
- 若上述关键能力缺失，严禁声称当前服务已通过 `2026-07-28` 规范一致性测试，此时应降级转用官方 Go SDK 客户端进行的集成测试与原生协议测试；
- 严禁自行自动升级测试套件、Node.js、npm 或项目内部的 SDK 依赖版本。建立新的基线版本时，必须查阅对应版本的 Release Notes 并同步更新本文档。
