---
metadata:
  external-cli: "true"
  cli-compatibility: "references/cli-compatibility.md"
name: tavily-web
description: 基于 Tavily API 的网页数据检索能力，通过环境变量 TAVILY_API_KEY 认证，提供实时网页搜索（search）、已知 URL 正文抽取（extract）、站点 URL 结构发现（map）、站点章节批量爬取（crawl）和多源带引用研究（research）。Use when 需要获取最新网页信息、查证新闻/版本/事实、读取某篇文章完整正文、收集某文档站的章节内容，或产出带来源引用的调研报告；触发词包括"搜一下网上"、"查最新"、"读这篇文章全文"、"把这个站点的文档收进来"、"做个深度研究"。不用于离线代码任务，也不用于不依赖外部信息的任务；使用前用户必须先配置 TAVILY_API_KEY 环境变量。
---

# Tavily Web

为不连接外部世界的 agent 提供取数路径：广度（search/map）→ 深度（extract/crawl）→ 综合（research）。

## 启动方式

先把本 `SKILL.md` 所在目录的绝对路径保存为 Skill 目录。不得假设当前工作目录就是 Skill 目录：

```bash
TAVILY_SKILL_DIR="/absolute/path/to/installed/tavily-web"
tv() { python3 "$TAVILY_SKILL_DIR/scripts/tavily.py" "$@"; }
```

工具为纯 Python 标准库脚本，无第三方依赖；凭据只读 `TAVILY_API_KEY` 环境变量。

## 前置检查（每次会话首次使用必做）

1. 运行 `tv check`。
   - 退出码 2：`TAVILY_API_KEY` 未配置或为空白。**只提示用户**：到 https://app.tavily.com 获取 key，然后 `export TAVILY_API_KEY="tvly-..."`；本 Skill 不代用户写 shell 配置，也不把 key 写入任何文件。等待用户配置完成后重跑 `tv check`。
   - 退出码 3：key 无效或过期，提示用户核对后更换。
   - 退出码 4：网络不可达，报告并停止。
2. `check` 正常返回前，不执行任何数据检索。

## 取数路由

| 需求 | 命令 | 说明 |
| --- | --- | --- |
| 发现来源、查当前事实 | `tv search "<query>"` | 默认 5 条、basic 深度；`--depth advanced` 换更深抓取；`--topic news --days N` 限新闻窗口；`--include-answer` 附 Tavily 摘要答案 |
| 已知 URL 读全文 | `tv extract <url> [url ...]` | 可一次传多个 URL；JS 重度页面 curl 拿不到正文时优先用它 |
| 知道站点不知道页面 | `tv map <url>` | 输出站点 URL 结构，再对目标页做 extract |
| 收整段文档/章节 | `tv crawl <url> [--max-depth N] [--max-breadth N]` | 同步返回结果（内置轮询仅为防御兑底）；控制规模用 `--max-depth`/`--max-breadth`；大站点先向用户确认爬取范围 |
| 多源带引用研究 | `tv research "<topic>" [--model mini\|pro\|auto]` | 异步任务自动轮询（最长 300s）；报告正文在 `content` 字段，引用来源在 `sources` 字段；`--no-wait` 只建任务；`tv research-status <request_id>` / `tv research-poll <request_id>` 续查 |

默认升级路径：search 发现 → extract 读全 → map+crawl 扩大面 → research 做综合。

## 结果组织

- 所有子命令输出 JSON；把 `results` 里的 `url`、`title`、`published_date` 等来源信息保留进最终回答，引用时给出链接。
- research 报告的正文（`content`）与来源列表（`sources`）整体呈现，不删引用；extract 失败 URL 看 `failed_results`。
- search 的 snippet 不足以回答时，对 top 1-2 条结果补一次 extract，不要重复 search 换关键词碰运气超过两次。

## 失败与降级

- 401/403：提示用户刷新 key，停止重试。
- 429：告知限流，建议稍后重试或减小 `--max-results`。
- 5xx：重试一次，仍失败则报告。
- 网络不可达（退出码 4）：改用用户本地已有信息作答，并**明确声明数据新鲜度边界**（截至 agent 训练/本地文件的时间点）。
- 任何情况下不得把 key 打印到输出、日志或文件。

## 验证

运行包内确定性测试（不触网）：

```bash
python3 -m unittest discover -s "$TAVILY_SKILL_DIR/tests"
```

版本漂移、能力探测与失败处理细则见 [CLI 兼容性契约](references/cli-compatibility.md)。
