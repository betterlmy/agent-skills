# CLI 兼容性

<!-- cli-compatibility-contract:v1 -->

| 字段 | 值 |
| --- | --- |
| 工具 | Draw.io Desktop CLI |
| 分发标识 | Draw.io Desktop |
| 本机验证版本 | `30.0.1`（本机命令为 `drawio`） |
| 验证日期 | `2026-07-30` |
| 版本策略 | 记录已验证版本，并对当前任务需要的导出格式做能力验证 |

本机验证版本只证明当前环境基线；Draw.io Desktop 的安装渠道和可执行文件名因平台而异。

## 关键能力

先运行 `draw.io --version` 或 `drawio --version`。再用临时、最小 `.drawio` 文件验证当前任务需要的 `-x`、`-f`、`-e`、`-t`、`-s` 和输出格式；仅查看版本号不能证明 Electron、字体或无头渲染可用。

PPT-safe SVG 还依赖 `pdftocairo`，它不属于 Draw.io 版本兼容性的替代证明。

## 版本不一致时

- 版本不同但所需导出能力通过：继续执行，并记录实际版本。
- PNG、SVG 或 PDF 导出行为不同：停止套用已知修复，保留原始输出和错误证据。
- CLI 不可用：使用浏览器 URL fallback 或只交付有效 `.drawio` 源文件。
- 不得未经用户授权安装桌面应用、系统包或启动容器。
