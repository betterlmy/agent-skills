# 时序图深入设计指南（Sequence Diagrams）

时序图用于在时间维度上直观展示参与者之间的消息交互、API 调用链路与生命周期状态。

## 核心参与者语法（Participants）

```mermaid
sequenceDiagram
    autonumber
    actor User as 终端用户
    participant API as 网关服务
    participant DB as 关系型数据库

    User->>API: 发起请求 POST /login
    activate API
    API->>DB: 查询用户凭证
    activate DB
    DB-->>API: 返回用户信息
    deactivate DB
    API-->>User: 登录成功并签发 JWT
    deactivate API
```

**参与者定义类型：**
- `actor`：代表真实的人类用户或外部系统角色
- `participant`：代表软件模块、微服务、网关或数据库

## 消息箭头语法速查

| 箭头语法 | 含义说明 |
|---|---|
| `->` | 无箭头的实线（同步发起） |
| `->>` | 带实心箭头的实线（同步调用请求） |
| `-->` | 无箭头的虚线（异步发起） |
| `-->>` | 带实心箭头的虚线（同步响应返回） |
| `-x` | 带叉号的实线（消息传输中丢失或失败） |
| `--x` | 带叉号的虚线（返回响应丢失） |
| `-)` | 异步事件发送（无等待即刻返回） |
| `--))` | 异步响应返回 |

## 逻辑分支与循环块控制

### 1. 条件分支（alt / else）
```mermaid
sequenceDiagram
    participant Client
    participant Server

    Client->>Server: 提交订单支付请求
    alt 账户余额充足
        Server-->>Client: 扣款成功并出票
    else 余额不足
        Server-->>Client: 返回 400 提示充值
    end
```

### 2. 可选流程（opt）
```mermaid
sequenceDiagram
    participant App
    participant Storage

    App->>Storage: 保存用户配置文件
    opt 用户勾选了云端自动同步
        App->>Storage: 异步上传配置至对象存储
    end
```

### 3. 循环遍历（loop）
```mermaid
sequenceDiagram
    participant Worker
    participant Queue

    loop 每隔 5 秒轮询一次
        Worker->>Queue: 拉取待处理任务
    end
```

### 4. 并行并发执行（par / and）
```mermaid
sequenceDiagram
    participant Gateway
    participant UserSvc
    participant OrderSvc

    Gateway->>Gateway: 收到聚合查询请求
    par 并发请求用户信息
        Gateway->>UserSvc: GET /user/1001
    and 并发请求订单列表
        Gateway->>OrderSvc: GET /orders?user=1001
    end
```

## 便签注解与高亮（Notes）

```mermaid
sequenceDiagram
    participant A as 客户端
    participant B as 服务端

    Note over A: 准备本地缓存
    Note over A,B: 数据包经过 TLS 双向加密传输
    Note right of B: 触发异步审计日志落盘
```
