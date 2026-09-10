# CLI 兼容性

<!-- cli-compatibility-contract:v1 -->

| 字段 | 值 |
| --- | --- |
| 工具 | Python 3 标准库（`scripts/tavily.py`，无第三方依赖）+ Tavily REST API |
| 分发标识 | 系统 `python3` CLI；端点基地址默认 `https://api.tavily.com`（可用 `TAVILY_BASE_URL` 覆盖） |
| 本机验证版本 | `Python 3.9.6`（macOS 系统 `/usr/bin/python3`） |
| 验证日期 | `2026-09-10` |
| 版本策略 | 记录已验证版本，以能力探测决定其他版本能否继续 |

本机验证版本是可复现基线，不等同于最低或最高支持版本。脚本要求 Python ≥ 3.9（argparse 子命令 `required`、f-string 之外未用 3.10+ 语法）。

## 端点验证状态

凭据为环境变量 `TAVILY_API_KEY`（Bearer 头）。以下字段语义均于 2026-09-10 用真实密钥实测确认：

| 端点 | 状态 | 证据 |
| --- | --- | --- |
| `POST /search` | 已验证 | 无密钥 401；有密钥 200，响应含 `results`（url/title/snippet）、`answer`、`images`、`follow_up_questions` |
| `POST /extract` | 已验证 | 入参 `urls` 数组；响应 `results`（成功，含 `raw_content`）+ `failed_results`（逐项含 `url`/`error`） |
| `POST /map` | 已验证 | 入参为 `url` 单字符串 + `max_depth`（**不是** `urls` 数组） |
| `POST /crawl` | 已验证 | 同步返回（首次响应即含 `results`）；`max_depth`/`max_breadth` 有效，`max_crawled_pages` 不支持；脚本内置轮询为防御性兑底，实测不会触发 |
| `POST /research` | 已验证 | 入参字段为 `input`（**不是** `query`）；`model` 可选 `mini`/`pro`/`auto`（缺省 auto）；返回 `request_id` + `status: pending` |
| `GET /research/{request_id}` | 已验证 | 完成后 `status: completed`；报告正文在 `content` 字段（Markdown + [n] 引用编号），来源数组为 `sources` |

401 语义为无密钥探测实测；429/5xx 处理为标准 HTTP 语义的防御性实现，尚未被实际观测到。若 Tavily 变更字段，以上表为修复基线。

## 关键能力探测

```bash
tv check          # 退出码 0 = 密钥有效 + /search 可达 + 响应可解析（消耗 1 次 search 额度）
```

确定性行为（已用包内测试覆盖，不触网）：参数解析、无密钥退出码 2 与配置指引、401/429/网络失败退出码 3/4、check 输出密钥脱敏。

## 退出码契约

| 退出码 | 含义 |
| --- | --- |
| 0 | 成功（含 `--no-wait` 建任务成功） |
| 2 | 配置错误：`TAVILY_API_KEY` 缺失或空白 |
| 3 | API 错误：401/403（key 无效/过期）、429（限流）、5xx、异步任务失败或轮询超时 |
| 4 | 网络错误（连接失败/超时） |

## 版本不一致时

- Python 3.9 以下或缺失：停止使用，报告实际 `python3 --version`；不得为运行本工具改装用户 Python。
- 401 持续出现：提示用户更换 `TAVILY_API_KEY`，不自动重试超过一次。
- 429：指数退避无效，直接告知用户并建议降低调用频率。
- `TAVILY_BASE_URL` 指向非官方端点：401/字段语义结论不适用，按该端点自身响应字段重新探测，并在本表补充记录。
- crawl/research 字段语义与实测不符：修正 `scripts/tavily.py` 的防御性字段名列表，并更新上方端点验证状态表。

不得为运行本工具安装任何依赖或修改用户环境。
