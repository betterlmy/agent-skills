# CLI 兼容性

<!-- cli-compatibility-contract:v1 -->

| 字段 | 值 |
| --- | --- |
| 工具 | Node.js（运行 `scripts/detect.mjs` 的运行时） |
| 分发标识 | 系统 `node` CLI，无 npm 包依赖 |
| 本机验证版本 | `v24.14.1` |
| 验证日期 | `2026-09-10` |
| 版本策略 | 记录已验证版本，以能力探测决定其他版本能否继续 |

本机验证版本是可复现基线，不等同于最低或最高支持版本。不要仅凭版本号推断兼容，也不要自动升级用户环境。

## 关键能力

本 Skill 唯一的自动化路径是 `audit` 命令调用包内检测脚本：

```bash
node <skill-dir>/scripts/detect.mjs [--json] [--strict] <file ...>
```

能力探测（已在本机 `v24.14.1` 验证）：

1. `node --version` 返回可用版本；脚本为无依赖 ESM（`.mjs`），要求 Node 支持原生 ESM 模块（Node 12.17+）。
2. 冒烟运行：`node scripts/detect.mjs --json <任一 examples/*.html>` 退出码为 `0`，JSON 输出含 `p0` 计数与逐文件 `files` 数组。
3. 退出码契约：默认模式下检测到 P0 也返回 `0`（findings 是数据，不是工具失败）；仅 `--strict` 下 P0 返回 `1`。消费 `--json` 输出的按 `p0` 字段判断，不依赖退出码。

## 版本不一致时

- Node 缺失或低于 12.17：停止 `audit` 的自动化路径，退回 `references/audit.md` 的人工清单（廉价感黑名单 + pre-flight 逐项核对），并报告当前环境缺少可运行的 Node。
- `detect.mjs` 运行报错（脚本或参数不兼容）：不要猜测 JSON 字段语义；退回人工清单，报告实际 `node --version` 与失败输出。
- 版本不同但冒烟通过：继续执行，并报告“版本未经本 Skill 基线（v24.14.1）验证”。

不得为运行本脚本安装 Node 或修改用户环境；安装必须获得用户明确授权。
