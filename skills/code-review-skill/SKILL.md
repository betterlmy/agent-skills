---
name: code-review-skill
description: |
  提供跨技术栈的全面代码审查指导，覆盖 React 19、Vue 3、Angular 17+、Svelte 5、Rust、TypeScript、Java、Java 8、PHP、Python、Django、FastAPI、Go、C#/.NET、Kotlin、Swift、NestJS、C/C++、Zig、CSS/Less/Sass、Qt 等。
  涵盖架构审查、性能评估、安全审计、代码异味反模式及各生态常见缺陷。
  Use when: 审查 Pull Request、进行 PR Review、代码审查、评审代码变更、建立团队审查规范、指导开发者、执行架构/安全/性能审查、检查代码质量、排查潜在 Bug。
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash      # 运行 lint/test/build 命令验证代码质量
  - WebFetch  # 查阅最新文档和最佳实践
---

# Code Review Skill

通过建设性反馈、系统性分析和协作改进，将代码审查从单纯的“门禁把关”转变为“知识共享”与工程演进。

## 适用场景

- 审查 Pull Request 和代码变更
- 为团队建立代码审查标准与规范
- 在审查过程中指导与帮助开发者提升
- 执行系统级或模块级架构审查
- 制定审查清单和团队编码准则
- 改善工程团队协作与代码质量
- 缩短代码审查交付周期并减少返工
- 持续维持高质量代码标准

## 核心原则

### 1. 审查心态

**审查的目标：**
- 尽早发现潜在缺陷与边界情况
- 确保代码长期可维护性与可读性
- 促进团队成员间的工程知识共享
- 统一并落实团队编码规范
- 优化模块设计与系统架构
- 建立健康的团队工程文化

**非审查目标：**
- 炫耀个人知识或技术优越感
- 纠结格式细节（交给 Linter/Formatter 自动处理）
- 无必要地阻碍正常交付进度
- 强行推行纯个人编程偏好

### 2. 高效反馈

**优质反馈的特征：**
- 具体且具可操作性（明确指出问题与改法）
- 启发性而非评判性（说明背后原理与权衡）
- 对事不对人（聚焦于代码本身而非作者）
- 平衡客观（不仅挑错，也对优秀设计给予认可）
- 区分优先级（明确区分阻断项与建议项）

反例与正例对比：

```markdown
[反例] "这里写错了。"
[正例] "多用户并发访问时此处可能产生竞态条件。建议在此处引入互斥锁（Mutex）进行保护。"

[反例] "为什么不用 X 模式？"
[正例] "考虑过使用 Repository 模式吗？这样可以显著提高该模块的单元测试便捷性。参考示例：[link]"

[反例] "重命名这个变量。"
[正例] "[轻微/nit] 建议将变量名 `uc` 替换为 `userCount` 以提升语义清晰度。如果保持原样也不影响合并。"
```

### 3. 审查范围

**人工重点审查内容：**
- 业务逻辑正确性与边界条件（off-by-one、空指针、资源释放等）
- 安全漏洞（SQL 注入、XSS、越权、敏感数据暴露等）
- 性能影响（N+1 查询、高频循环、内存泄漏、大对象拷贝）
- 单元测试覆盖率与测试用例质量
- 错误与异常处理机制
- 关键模块注释与外部文档
- API 契约设计与符号命名
- 架构契合度与分层职责划分

**无需人工花费时间的范围：**
- 代码缩进与格式排版（统一由 Prettier、Black、gofmt 等工具处理）
- Import 排序与分组
- 基础 Lint 规范违规
- 简单的拼写检查

## 审查流程

### 第一阶段：上下文收集（2-3 分钟）

在深入代码之前，先了解整体背景：
1. 阅读 PR 描述和关联的 Issue/需求单
2. 检查 PR 规模（若超过 400 行，建议拆分）
3. 查看 CI/CD 状态（测试与静态检查是否已全部通过）
4. 明确当前变更对应的核心业务需求
5. 了解相关的架构决策与改动边界

> 针对大型 diff，可通过管道传入脚本 [`scripts/pr-analyzer.py`](scripts/pr-analyzer.py) 进行复杂度分级并获取建议路径：
> `git diff main...HEAD | python scripts/pr-analyzer.py`

### 第二阶段：宏观审查（5-10 分钟）

1. **架构与设计**：当前方案是否优雅贴切地解决了目标问题？
   - 涉及重大改动时，查阅 [架构审查指南](reference/architecture-review-guide.md)
   - 检查 SOLID 原则、高内聚低耦合、是否存在设计反模式
2. **性能评估**：是否存在潜在性能瓶颈？
   - 对性能敏感路径，查阅 [性能审查指南](reference/performance-review-guide.md)
   - 检查算法复杂度、数据库 N+1 查询、内存开销
3. **组织结构**：新建文件是否放置在合适目录？分层是否清晰？
4. **测试策略**：是否有针对正常逻辑与边界用例的自动化测试？

### 第三阶段：逐行审查（10-20 分钟）

逐个文件核对：
- **逻辑与正确性**：边界检查、off-by-one、空值/nil 处理、并发竞态、超时与重试
- **安全性**：参数校验、注入防范、XSS 防护、敏感数据日志脱敏
- **性能**：N+1 查询、低效循环、内存泄漏、大对象频繁分配
- **可维护性**：语义清晰的命名、单一职责、关键逻辑注释
- **代码复用**：接受新代码前，优先检索仓库中已有公用方法与辅助函数，避免重复造轮子。参阅 [通用质量指南](reference/code-quality-universal.md) 排查参数膨胀、抽象泄露、深层嵌套、弱类型字符串滥用、TOCTOU 和无效更新等反模式

### 第四阶段：总结与结论（2-3 分钟）

1. 概述核心关注点与改进项
2. 对写得好的构思与设计给予明确肯定
3. 给出清晰明确的审查结论：
   - [通过 / Approve]：可以合并
   - [评论 / Comment]：非阻断性轻微建议
   - [需要修改 / Request Changes]：存在必须修复的缺陷
4. 若涉及复杂修改，主动提议结对或针对性讨论

## 审查技巧

### 技巧 1：清单法（Checklist）

通过系统化清单保证审查维度一致性。详细安全核对项见 [安全审查指南](reference/security-review-guide.md)。

### 技巧 2：启发提问法

采用提问代替武断断言：

```markdown
[反例] "列表为空时这里会崩溃。"
[正例] "如果 `items` 是空数组，这里的预期行为是什么？"

[反例] "你这里必须补异常处理。"
[正例] "如果下游 API 调用失败并返回超时，这个流程应该如何处理？"
```

### 技巧 3：协作建议法

使用协作平等的沟通语气：

```markdown
[反例] "必须改用 async/await。"
[正例] "建议：改用 async/await 或许能让这段异步逻辑更直观，你觉得如何？"

[反例] "把这个提成独立函数。"
[正例] "这段逻辑在 3 个地方重复出现，是否可以考虑抽取为公共辅助函数？"
```

### 技巧 4：标明严重级别

使用统一前缀标签明确反馈的紧迫程度：

- `[阻断 / blocking]`：合并前必须修复的问题（功能 Bug、安全漏洞等）
- `[重要 / important]`：建议修复的问题，若有异议可讨论
- `[轻微 / nit]`：细节打磨或个人建议，不阻断合并
- `[建议 / suggestion]`：可供参考的备选实现方案
- `[探讨 / learning]`：工程知识交流或经验探讨，无需修改代码
- `[赞赏 / praise]`：优秀的代码实现或优雅的设计

**严重级别层级：** `[blocking]` / `[important]` / `[nit]` 为核心三级体系。其余标签属于非阻断性注解。

## 语言专项审查指南

根据审查的目标语言与框架，查阅对应的详细专项指南：

| 语言 / 框架 | 参考文档 | 核心关注领域 |
|---|---|---|
| **React** | [React 指南](reference/react.md) | Hooks 规范、useEffect 依赖、React 19 Actions、RSC、Suspense、TanStack Query v5 |
| **Vue 3** | [Vue 指南](reference/vue.md) | Composition API、响应式系统、Props/Emits、Watchers、Composables 规范 |
| **Angular 17+** | [Angular 指南](reference/angular.md) | Signals、Standalone 组件、RxJS、Zoneless、模板性能优化、路由守卫、HttpInterceptor |
| **Rust** | [Rust 指南](reference/rust.md) | 所有权与借用检查、Unsafe 审计、异步编程、取消安全、错误处理体系 |
| **TypeScript** | [TypeScript 指南](reference/typescript.md) | 严格类型安全、async/await、不可变性保障、模块解析、TS 5.x 特性 |
| **Python** | [Python 指南](reference/python.md) | 可变默认参数陷阱、异常处理规范、类型注解、类属性与生命周期 |
| **Django / DRF** | [Django 指南](reference/django.md) | 安全审计、N+1 查询、Serializer 反模式、ViewSet 规范、异步视图 |
| **FastAPI** | [FastAPI 指南](reference/fastapi.md) | Depends 依赖注入、Pydantic v2 校验、异步正确性、DB 会话/N+1、认证与鉴权边界 |
| **Java** | [Java 指南](reference/java.md) | Java 17/21 新特性、Spring Boot 3、虚拟线程、Stream/Optional 正确用法 |
| **Java 8 / Legacy** | [Java 8 指南](reference/java8.md) | Java 8 基线、Spring Boot 2、javax.* 迁移、java.time 规范、CompletableFuture |
| **PHP** | [PHP 指南](reference/php.md) | PHP 8.x 类型系统、PDO 预编译、安全审查、Composer 依赖、PHPUnit/PHPStan |
| **C# / .NET** | [C# 指南](reference/csharp.md) | C# 12 特性、异步编程、EF Core 查询性能、ASP.NET Core 架构、LINQ 开销 |
| **Go** | [Go 指南](reference/go.md) | 错误处理与包装、goroutine/channel 并发、Context 传递、接口设计 |
| **Kotlin / Android** | [Kotlin 指南](reference/kotlin.md) | 协程作用域、Flow、Jetpack Compose、空安全、内存泄漏防护、架构模式 |
| **Swift / SwiftUI** | [Swift 指南](reference/swift.md) | Optionals、Swift Concurrency、Sendable/Actors、SwiftUI 属性包装器、值类型与引用类型 |
| **NestJS** | [NestJS 指南](reference/nestjs.md) | 依赖注入生命周期、分层架构、DTO 校验、Guard/Interceptor、循环依赖治理 |
| **Svelte / SvelteKit** | [Svelte 指南](reference/svelte.md) | Runes 响应式、Load 函数、Form Actions、Store 迁移、SSR/CSR 边界处理 |
| **C** | [C 指南](reference/c.md) | 指针与缓冲区边界、内存安全、未定义行为（UB）、安全编码规范、跨平台可移植性 |
| **C++** | [C++ 指南](reference/cpp.md) | RAII 资源管理、智能指针生命周期、C++20/23 特性、constexpr、异常安全 |
| **Zig** | [Zig 指南](reference/zig.md) | 内存分配器（Allocators）、错误联合类型、defer/errdefer、comptime、C 互操作 |
| **CSS / Less / Sass** | [CSS 指南](reference/css-less-sass.md) | 变量体系、!important 禁令、渲染性能优化、响应式断点、现代浏览器兼容性 |
| **Qt** | [Qt 指南](reference/qt.md) | 对象模型生命周期、信号与槽、Model/View 架构、QML 交互、Qt6 迁移 |

## 跨横切面通用指南

适用于所有编程语言的通用审查模式与质量规范：

| 审查领域 | 参考文档 | 核心关注重点 |
|---|---|---|
| **架构审查** | [架构审查指南](reference/architecture-review-guide.md) | SOLID 原则、架构反模式、耦合度与内聚度、依赖倒置方向 |
| **性能审查** | [性能审查指南](reference/performance-review-guide.md) | Web Vitals 指标、N+1 查询、算法复杂度、内存泄漏排查、缓存策略 |
| **安全审查** | [安全审查指南](reference/security-review-guide.md) | SQL 注入、XSS、CSRF、SSRF、IDOR 越权、命令注入、跨语言安全模式 |
| **通用代码质量** | [通用代码质量指南](reference/code-quality-universal.md) | 代码复用审计、参数膨胀、抽象泄漏、多层嵌套、弱类型字符串、TOCTOU、冗余状态 |
| **常见缺陷排查** | [常见缺陷清单](reference/common-bugs-checklist.md) | 各语言典型 Bug 模式、高频陷阱与防范清单 |
| **SQL 注入防范** | [SQL 注入防范指南](reference/cross-cutting/sql-injection-prevention.md) | 参数化查询、ORM 安全用法、动态标识符拼接防范、跨语言示例 |
| **XSS 防范** | [XSS 防范指南](reference/cross-cutting/xss-prevention.md) | 输出编码、CSP 策略、框架防范差异、输入校验与输出转义边界 |
| **N+1 查询治理** | [N+1 查询治理指南](reference/cross-cutting/n-plus-one-queries.md) | 预加载（Eager loading）、批量拉取（Batch fetching）、DataLoader 机制 |
| **错误处理原则** | [错误处理原则指南](reference/cross-cutting/error-handling-principles.md) | 快速失败（Fail fast）、错误层级划分、反模式识别、结构化日志记录 |
| **并发与异步模式** | [并发与异步模式指南](reference/cross-cutting/async-concurrency-patterns.md) | Goroutines、async/await、Actors、结构化并发、跨语言并发安全 |
| **审查最佳实践** | [代码审查最佳实践](reference/code-review-best-practices.md) | 审查沟通技巧、审查者心态、建设性反馈、标签使用规范 |

## 附加资源

- [PR 审查评论模板](assets/pr-review-template.md) - 标准化 PR 审查输出模板
- [快速审查清单](assets/review-checklist.md) - 常用核对清单速查
