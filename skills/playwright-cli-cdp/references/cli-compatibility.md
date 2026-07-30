# CLI 兼容性

<!-- cli-compatibility-contract:v1 -->

| 字段 | 值 |
| --- | --- |
| 工具 | playwright-cli |
| 分发标识 | `@playwright/cli` |
| 本机验证版本 | `0.1.17` |
| 验证日期 | `2026-07-30` |
| 版本策略 | 记录已验证版本，以环境检查和命令能力决定其他版本能否继续 |

本机验证版本是当前文档、wrapper 和示例的可复现基线，不是未经跨版本测试得出的支持范围。

## 关键能力

运行 `scripts/check-environment.sh` 或 `scripts/check-environment.ps1`。检查会验证版本输出，并确认 `attach`、`snapshot`、`run-code`、`tracing-start` 和 `video-start` 出现在帮助中。

只有任务实际使用的命令和选项通过帮助或无副作用试运行后，才能认为该路径可用。`page.screencast` 等注入 API 不是标准 Playwright API，使用前还要按对应参考文档验证实际行为。

## 版本不一致时

- 版本不同但所需能力存在：继续执行，报告该版本未经当前基线验证。
- 命令存在但选项变化：以当前 `--help` 为准调整调用，不得把文档示例当成运行时事实。
- 关键命令缺失：停止对应工作流并报告缺失能力；不要用 DOM 或直接接口绕过 UI 验收目标。
- 安装或升级会修改用户环境，必须先获得用户同意。

需要复现当前基线且用户已授权安装时，可使用：

```bash
npm install -g @playwright/cli@0.1.17
```
