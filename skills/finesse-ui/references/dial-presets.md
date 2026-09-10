# Quick-Start Dial Mapping & Workbench Resolver

## Quick-Start Dial Mapping

If the brief contains these cues, use these presets as a starting point before refining:

| User says | SOUL | SPECTACLE | DENSITY |
|-----------|------|-----------|---------|
| "premium", "luxury", "high-end" | 8 | 5 | 3 |
| "minimal", "clean", "understated" | 6 | 3 | 3 |
| "bold", "striking", "impactful" | 7 | 7 | 4 |
| "editorial", "magazine", "publication" | 8 | 4 | 6 |
| "tech", "AI", "SaaS" marketing | 6 | 7 | 5 |
| "corporate", "B2B", "enterprise" | 4 | 3 | 6 |
| "playful", "vibrant", "creative" | 7 | 6 | 5 |
| "data-heavy", "dashboard", "analytics" | 4 | 2 | 9 |
| "商家后台", "管理后台", "admin console", "back-office" | 5 | 2 | 7 |
| **"工作台" 裸词，没有别的线索** | **—** | **—** | **—** ← 不套用任何一行，先问它围着什么转（下方解析器） |
| **工作台 · 电脑上开** — "工作台", "值守台", "控制台", "专属工作台" | 6 | 2 | 6–7 |
| **工作台 · 手机上开** — "每日工作台", "打卡页", "记录页", "daily desk" *(h5 · morph A.1)* | 6 | 2 | 4–5 |
| ↳ **叠加项**：有 agent 替他跑活 — "AI 工作台", "agent console", "智能体控制台", "copilot UI" | — | — | **+1** ← 不换行，在上面两行之上加 `ai-console.md` 的机械层 |
| "发布/创建流程", "wizard", "publish flow", "配置", "settings" | 4 | 1 | 7 |
| "landing page" (no other cues) | 7 | 6 | 4 |
| "portfolio" | 8 | 6 | 3 |
| "product page", "PDP", "product detail" | 6 | 4 | 6 |
| "商品列表", "PLP", "category page", "marketplace" | 3 | 2 | 8 |
| "app 原型", "app screen", "移动端 app UI" *(h5 · morph A)* | 6 | 3 | 6–8 |
| "活动页", "H5 营销页", "campaign H5" *(h5 · morph B)* | 8 | 6 | 3–4 |
| "报告 H5", "年度报告", "data report H5" *(h5 · morph C)* | 8 | 6 | 5 |
| "移动端商详", "mobile PDP" *(h5 · morph D)* | 6 | 3 | 8 |
| "手机官网", "mobile site" *(h5 · morph E)* | 7 | 5 | 6 |
| "天气/海报类单屏", "ambient screen" *(h5 · morph F)* | 9 | 7–8 | 2–3 |

Override these immediately if the brief provides stronger or contradicting signals. The h5 rows set the dials for the *morphology* (`h5-mobile.md` §0); the wrapped content register may adjust them.

---

## 后台 vs 工作台 — One Fork, Then Two Modifiers

**「工作台」 and 「后台」 are two different products.** Everything else people say — 个人工作台 · AI 工作台 · 每日工作台 · 值守台 · 控制台 — is one of these two wearing a modifier. Resolve it in three steps, in order:

### ① 围着什么转 — This is the fork, and the only one:

| | **后台 back-office** | **工作台 workbench** |
|---|---|---|
| 围着什么转 | **一批业务对象** — N 个客户 · 订单 · 设备 · 工单 · 学员 | **他自己反复在做的一件事** — 记账 · 训练 · 带娃 · 写作 · 值守 · 处理异常单 |
| 为什么打开 | 有活要处理：来单了、告警了、该出报表了 | 到点了，回来看一眼 · 记一笔 · 收个尾 |
| 数据谁写 | 系统、对接、别人 | **他自己**，几秒钟，成本必须接近零 |
| 性格 | **中性是义务** — 它活在别人的品牌里，旁边还有十一个工具 | **必须有** — 这是他的台子，中性的没有第二次打开的理由 |
| 建法 | `product-ui.md`（+ `workflow-ui.md` 如果主动作是提交/发布） | 下面第 ② 步选载体 |

### ② 在哪开 — 这只决定载体，不换物种

工作台是一个东西、两副身体：

| 载体 | 壳 | 例子 |
|---|---|---|
| **电脑上开** | `product-ui.md` 的 shell，但带 A.1 的性格和克制的密度 —— **不是一个塞满图表的 dashboard** | `examples/relay-agent-console.html` |
| **手机上开** | `h5-mobile.md` morph **A.1**，锁定手机框 + TabBar，DENSITY 4–5 | `examples/h5-fern-meal-desk.html` · `h5-peach-daily-desk.html` |

### ③ 有没有东西替他干活 — 这是能力层，跟①②正交

如果有 agent 在跑、输出是流式的、跑一半会失败、有队列 —— **叠加** `ai-console.md` 的机械层（运行流 · 九个运行状态 · 常驻停止 · 流内审批卡 · 成本回执）。**它不是第三个物种，是工作台可以带的一种能力**，桌面和手机两副身体都能带（`ai-console.md` §8 是桌面壳，§9 是手机形态）。一个没有 agent 的工作台不用加这层；一个后台接了 agent 也不会因此变成工作台。

### 两个不是判据的东西，别拿它们当判据

- **人数**：一家人共用的记账台、一个小组共用的值守台，都是工作台；一个人独用的进销存，仍然是后台。
- **屏幕**：它只在第 ② 步决定长什么样，从来不决定这是什么。

### When the brief is just 「工作台」 with nothing else:

Ask, don't guess:

```
这个台子主要围着什么转？
一批客户/订单/设备这类东西 · 你自己反复在做的一件事（记账、值守、带娃…）
```

Defaulting 「工作台」 to a back-office is the single most likely mis-build in this skill.
