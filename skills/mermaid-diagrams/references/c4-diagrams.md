# C4 软件架构图设计指南（C4 Architecture）

C4 模型是一种通过不同抽象层级描述软件架构的经典方法论，包含：上下文（Context）、容器（Container）、组件（Component）与代码（Code）。Mermaid 提供了针对 C4 语法的原生支持。

## 1. 系统上下文图（System Context - C4Context）

展示目标系统与外部用户、第三方系统之间的宏观边界：

```mermaid
C4Context
    title 银行在线核心系统上下文视图

    Person(customer, "银行客户", "使用网页或移动 App 进行转账和查询")
    System(banking_system, "核心网银系统", "允许客户查看账户信息并执行交易")
    System_Ext(mail_system, "第三方邮件服务", "负责外发验证码与流水邮件")
    System_Ext(mainframe, "大型机总账系统", "存储所有银行账户核心流水与结余")

    Rel(customer, banking_system, "访问并操作", "HTTPS")
    Rel(banking_system, mail_system, "发送通知邮件", "SMTP")
    Rel(banking_system, mainframe, "读写账户主账", "TCP/IP")
```

## 2. 容器图（Container - C4Container）

展开系统内部的高层技术架构（如前端单页应用、后端 API、数据库）：

```mermaid
C4Container
    title 核心网银系统容器视图

    Person(customer, "银行客户", "持有个人账户的用户")

    System_Boundary(c1, "核心网银系统边界") {
        Container(spa, "单页 Web 应用", "React, TypeScript", "提供核心用户操作交互界面")
        Container(mobile, "移动客户端", "Flutter", "iOS 与 Android 原生客户端")
        Container(backend_api, "业务 API 服务", "Go, Gin", "处理转账、认证与核心业务逻辑")
        ContainerDb(database, "关系型数据库", "PostgreSQL", "持久化存储用户、账户与流水")
    }

    Rel(customer, spa, "通过浏览器访问", "HTTPS")
    Rel(customer, mobile, "通过手机操作")
    Rel(spa, backend_api, "调用接口", "JSON/HTTPS")
    Rel(mobile, backend_api, "调用接口", "JSON/HTTPS")
    Rel(backend_api, database, "读写业务数据", "SQL/TCP")
```

## 3. 组件图（Component - C4Component）

聚焦在单个微服务容器内部，展示内部模块与关键职责划分：

```mermaid
C4Component
    title 业务 API 服务内部组件视图

    Container_Boundary(b1, "业务 API 服务内部") {
        Component(auth_controller, "认证控制层", "REST Handler", "处理用户登录与 Token 刷新")
        Component(account_service, "账户业务领域服务", "Go Struct", "处理账户余额划转与冻结")
        Component(security_component, "安全拦截器", "Middleware", "校验 JWT 签名与角色权限")
        Component(repo, "数据库仓储层", "GORM/SQL", "负责与 PostgreSQL 交互")
    }

    Rel(auth_controller, security_component, "触发签名验证")
    Rel(auth_controller, account_service, "调用业务流水")
    Rel(account_service, repo, "持久化变更")
```
