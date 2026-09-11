---
metadata:
  external-cli: "true"
  cli-compatibility: "references/cli-compatibility.md"
name: find-skills
description: 帮助用户在开放 Agent Skill 生态中发现并安装扩展能力。Use when 用户提出“怎么做某事”、“帮我找一个某功能的 skill”、“有没有能做某事的 skill”，或希望扩展 Agent 自身能力时；不用于已知并直接修改现有本地 Skill 的任务。
---

# Find Skills

本 Skill 用于帮助用户在开放的 Agent Skill 生态系统中发现、评估并安装适配业务场景的专业 Skill。

## 适用场景

当用户表达以下意图时触发本 Skill：

- 询问“我该如何做某事”，且该场景很可能是已有公共 Skill 覆盖的通用任务；
- 明确说“帮我找一个用于某功能的 skill”或“是否有针对某任务的 skill”；
- 询问“你能不能做某某专业操作”，且属于特定领域的专项扩展能力；
- 明确希望扩展当前 Agent 的功能、工具集或工作流；
- 寻找特定领域的脚手架模板、自动化流程或专业指令包；
- 提及希望在设计、测试、部署、文档等垂直领域获得专业指导。

## 什么是 Skills CLI？

Skills CLI（`npx skills`）是开放 Agent Skill 生态系统的包管理工具。Skill 是模块化的能力扩展包，能为 Agent 赋予专项领域的先验知识、标准工作流和自动化工具。

依赖这些命令前，先阅读 [CLI 兼容性契约](references/cli-compatibility.md) 并尝试 `npx --no-install skills --help`。若当前机器未预装 Skills CLI，说明命令可用性尚未验证。未经用户明确授权，不得擅自让 `npx` 下载新包。

**核心命令清单：**

- `npx skills find [query]`：通过关键字搜索或交互式浏览 Skill；
- `npx skills add <package>`：从 GitHub 仓库或其他源安装指定的 Skill；
- `npx skills check`：检查已安装 Skill 的版本更新；
- `npx skills update`：更新所有已安装的 Skill。

**生态探索主页：** https://skills.sh/

## 查找 Skill 标准流程

### 第一步：明确用户真实诉求

当用户寻求特定帮助时，先梳理出三要素：
1. **所属技术领域**：例如 React、单元测试、UI 设计、CI/CD 自动化等；
2. **具体执行任务**：例如编写 E2E 测试、制作交互动效、执行 PR 代码审查等；
3. **普遍性评估**：该诉求是否属于业内常见痛点（是否大概率已有现成成熟方案）。

### 第二步：优先排查官方榜单

在直接运行命令行搜索前，可先查阅 [skills.sh 排行榜](https://skills.sh/)，了解该领域是否已有广受认可的成熟 Skill。排行榜按真实安装量排序，能快速筛选出高可用、经受充分验证的优质方案。

例如常见的优质官方源包括：
- `vercel-labs/agent-skills`：专注 React、Next.js、现代前端设计（数十万级安装量）；
- `anthropics/skills`：涵盖前端工程、文档解析、数据处理等。

### 第三步：针对性检索 Skill

若排行榜未直接命中需求，执行搜索命令：

```bash
npx skills find [关键词]
```

检索示例：
- 用户提问“如何让我的 React 应用跑得更快？” → `npx skills find react performance`
- 用户询问“你能帮我审查 PR 吗？” → `npx skills find pr review`
- 用户需要“生成规范的更新日志” → `npx skills find changelog`

### 第四步：质量与安全性严格评估

**严禁仅凭搜索结果列表就直接盲目推荐。** 推荐前必须严格把关：

1. **安装量规模**：优先推荐安装量在 1,000+ 以上的成熟包；对安装量低于 100 的包保持谨慎；
2. **发布者信誉**：来自知名机构或知名开源团队（如 `vercel-labs`、`anthropics`、`microsoft`）的包具有更高可靠性；
3. **GitHub Star 数**：查看源码仓库，若 Star 数极低且无长期维护，应向用户提示潜在风险。

### 第五步：向用户规范呈现方案

定位到符合要求的 Skill 后，向用户结构化呈现以下信息：

1. Skill 名称与核心定位；
2. 安装量数据与来源作者/组织；
3. 推荐安装的具体命令；
4. 查阅详细介绍的链接（skills.sh 详情页）。

呈现示例：

```markdown
找到一个契合当前需求的 Skill：`react-best-practices`
该 Skill 沉淀了 Vercel 工程团队总结的 React 与 Next.js 性能优化实战准则（累计安装量 185K+）。

安装命令：
npx skills add vercel-labs/agent-skills@react-best-practices

详细说明：https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### 第六步：经授权后代为安装

当用户明确确认希望安装时，可执行安装命令：

```bash
npx skills add <owner/repo@skill> -g -y
```

其中 `-g` 参数表示全局安装（用户级别），`-y` 参数用于自动跳过交互式确认提示。

## 常见技能分类与检索词

在进行检索时，可参考以下常用分类词汇：

| 分类领域 | 推荐检索关键词 |
|---|---|
| Web 前端开发 | react, nextjs, typescript, css, tailwind |
| 质量保障与测试 | testing, jest, playwright, e2e, vitest |
| 运维与交付（DevOps） | deploy, docker, kubernetes, ci-cd |
| 文档与规范 | docs, readme, changelog, api-docs |
| 代码质量治理 | review, lint, refactor, best-practices |
| UI/UX 设计 | ui, ux, design-system, accessibility |
| 工程效能提升 | workflow, automation, git |

## 高效检索建议

1. **使用具体限定词**：如“react testing”相比宽泛的“testing”更能精确定位；
2. **尝试近义词与缩写**：若“deploy”无结果，可尝试“deployment”或“ci-cd”；
3. **查阅知名聚合仓库**：许多高质量能力集成在成熟的开源合集中。

## 未找到适配 Skill 时的处理

若检索后确认生态中暂无现成适配方案：

1. 如实告知用户当前暂未检索到现成的专门 Skill；
2. 主动说明可以直接利用 Agent 自身通用编程与推理能力协助用户解决当前问题；
3. 若该场景是用户的高频业务需求，可建议用户使用 `npx skills init` 初始化定制专属于自己的 Skill。

回复示例：

```markdown
在公共生态中未检索到与“某某功能”直接匹配的成熟 Skill。
不过无需担心，我可以直接凭借通用工程能力为您处理该需求！是否现在开始？

如果您经常需要重复此项特定流程，后续也可以考虑将其封装为独立 Skill：
npx skills init my-custom-skill
```
