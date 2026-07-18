---
name: go-mcp-builder
description: 用 Golang 编写 MCP (Model Context Protocol) server 的完整指南，使用 mark3labs/mcp-go SDK 和 Streamable HTTP 传输层。当用户要开发、修改或调试 Go MCP server 时必须调用此 skill，包括：新建 MCP 项目、添加 Tool/Resource/Prompt、配置 HTTP 传输、处理认证、中间件开发等场景。
tags: [go, mcp, mcp-server, mark3labs, streamable-http]
---

## 技术栈

- **语言**: Go 1.21+
- **SDK**: `github.com/mark3labs/mcp-go`
- **传输层**: Streamable HTTP（默认端点 `/mcp`）
- **命名规范**: 遵循 `go-coding-standards` skill

---

## 项目结构

```
my-mcp-server/
├── main.go                  # 入口：创建 server、注册能力、启动 HTTP
├── server/
│   └── server.go            # 初始化 MCPServer，统一注册所有 tool/resource/prompt
├── tools/
│   ├── tools.go             # 汇总注册函数
│   └── <domain>.go          # 每个业务域一个文件，如 file.go、search.go
├── resources/
│   └── resources.go
├── prompts/
│   └── prompts.go
└── go.mod
```

每个功能模块导出 `RegisterXxx(s *server.MCPServer)` 函数，在 `server/server.go` 中统一调用。

---

## 初始化与启动

```go
// go.mod
module my-mcp-server

go 1.21

require github.com/mark3labs/mcp-go v0.x.x
```

```go
// main.go
package main

import (
    "log"
    "net/http"

    "my-mcp-server/server"
    mcpserver "github.com/mark3labs/mcp-go/server"
)

func main() {
    s := server.New()

    httpServer := mcpserver.NewStreamableHTTPServer(s,
        mcpserver.WithEndpointPath("/mcp"),
        mcpserver.WithStateLess(true),
    )

    log.Println("MCP server listening on :8080")
    if err := httpServer.Start(":8080"); err != nil {
        log.Fatalf("server error: %v", err)
    }
}
```

```go
// server/server.go
package server

import (
    "my-mcp-server/tools"
    "my-mcp-server/resources"
    "my-mcp-server/prompts"

    mcpserver "github.com/mark3labs/mcp-go/server"
)

// New 创建并初始化 MCP server，注册所有能力
func New() *mcpserver.MCPServer {
    s := mcpserver.NewMCPServer(
        "my-mcp-server",
        "1.0.0",
        mcpserver.WithToolCapabilities(true),
        mcpserver.WithResourceCapabilities(true, false),
        mcpserver.WithPromptCapabilities(true),
        mcpserver.WithRecovery(), // panic 自动恢复，生产环境必开
    )

    tools.Register(s)
    resources.Register(s)
    prompts.Register(s)

    return s
}
```

---

## 注册 Tool

Tool 是 MCP 的核心能力，对应 LLM 可调用的操作。

```go
// tools/file.go
package tools

import (
    "context"
    "fmt"

    "github.com/mark3labs/mcp-go/mcp"
    mcpserver "github.com/mark3labs/mcp-go/server"
    log "github.com/sirupsen/logrus"
)

// registerFileTools 注册文件相关工具
func registerFileTools(s *mcpserver.MCPServer) {
    readFileTool := mcp.NewTool("read-file",
        mcp.WithDescription("读取指定路径的文件内容"),
        mcp.WithString("path",
            mcp.Required(),
            mcp.Description("文件的绝对或相对路径"),
        ),
        mcp.WithNumber("max_lines",
            mcp.Description("最多读取的行数，默认读取全部"),
        ),
    )
    s.AddTool(readFileTool, handleReadFile)
}

func handleReadFile(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
    log.Infof("=== handleReadFile in ===")
    log.Infof("request: %+v", req)

    defer func() {
        log.Infof("=== handleReadFile out ===")
    }()

    path, err := req.RequireString("path")
    if err != nil {
        return mcp.NewToolResultError(err.Error()), nil
    }

    maxLines, _ := req.Int("max_lines")

    // 业务逻辑...
    content := fmt.Sprintf("file content of %s (max %d lines)", path, maxLines)

    return mcp.NewToolResultText(content), nil
}
```

```go
// tools/tools.go
package tools

import mcpserver "github.com/mark3labs/mcp-go/server"

// Register 注册所有 tool
func Register(s *mcpserver.MCPServer) {
    registerFileTools(s)
    // registerSearchTools(s)
}
```

### Tool Handler 规范

- **日志**：每个 handler 打 `=== handlerName in/out ===` 边界标记，入参用 `%+v` 记录
- **参数错误**（类型不对、必填缺失）：返回 `mcp.NewToolResultError(msg)`，不返回 Go error
- **业务错误**（资源不存在、调用失败）：同上，错误描述返回给 LLM，由 LLM 决策下一步
- **系统级错误**（panic、不可恢复）：返回 Go `error`，由 `WithRecovery` 兜底

### Schema 类型对照

| 参数类型 | mcp 函数 |
|---------|---------|
| string  | `mcp.WithString("name", ...)` |
| number  | `mcp.WithNumber("name", ...)` |
| bool    | `mcp.WithBoolean("name", ...)` |
| []string | `mcp.WithArray("name", mcp.WithStringItems())` |
| object  | `mcp.WithObject("name", mcp.WithStringProperty("key"))` |

参数约束选项：`mcp.Required()`、`mcp.Description("...")`、`mcp.Enum("a","b","c")`

### 参数提取方式

```go
// 必填参数，缺失时返回 error
val, err := req.RequireString("name")
val, err := req.RequireFloat("count")
val, err := req.RequireBool("flag")

// 可选参数，不存在时返回零值
val, _ := req.String("name")
val, _ := req.Int("count")
val, _ := req.Bool("flag")
```

---

## 注册 Resource

Resource 用于暴露数据（文件、数据库记录等），LLM 通过 URI 读取。

```go
// resources/resources.go
package resources

import (
    "context"

    "github.com/mark3labs/mcp-go/mcp"
    mcpserver "github.com/mark3labs/mcp-go/server"
)

// Register 注册所有 resource
func Register(s *mcpserver.MCPServer) {
    configResource := mcp.NewResource(
        "config://app",
        "应用配置",
        mcp.WithMIMEType("application/json"),
        mcp.WithResourceDescription("返回当前应用的运行时配置"),
    )
    s.AddResource(configResource, handleConfigResource)
}

func handleConfigResource(ctx context.Context, req mcp.ReadResourceRequest) ([]mcp.ResourceContents, error) {
    content := `{"env":"production","version":"1.0.0"}`
    return []mcp.ResourceContents{
        mcp.TextResourceContents{
            URI:      req.Params.URI,
            MIMEType: "application/json",
            Text:     content,
        },
    }, nil
}
```

---

## 注册 Prompt

Prompt 是可复用的提示词模板，带参数。

```go
// prompts/prompts.go
package prompts

import (
    "context"
    "fmt"

    "github.com/mark3labs/mcp-go/mcp"
    mcpserver "github.com/mark3labs/mcp-go/server"
)

// Register 注册所有 prompt
func Register(s *mcpserver.MCPServer) {
    s.AddPrompt(
        mcp.NewPrompt("code-review",
            mcp.WithPromptDescription("生成代码审查提示词"),
            mcp.WithArgument("language", mcp.ArgumentDescription("编程语言，如 go、python")),
            mcp.WithArgument("focus", mcp.ArgumentDescription("审查重点，如 security、performance")),
        ),
        handleCodeReview,
    )
}

func handleCodeReview(ctx context.Context, req mcp.GetPromptRequest) (*mcp.GetPromptResult, error) {
    lang := req.Params.Arguments["language"]
    focus := req.Params.Arguments["focus"]

    return mcp.NewGetPromptResult(
        "代码审查",
        []mcp.PromptMessage{
            mcp.NewPromptMessage(
                mcp.RoleUser,
                mcp.NewTextContent(fmt.Sprintf(
                    "请对以下 %s 代码进行审查，重点关注 %s 方面。", lang, focus,
                )),
            ),
        },
    ), nil
}
```

---

## 中间件

中间件用于在 tool handler 执行前后插入横切逻辑（日志、鉴权、限流等）。

```go
// 中间件类型：包装 ToolHandlerFunc
type ToolHandlerFunc func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error)
```

### 自定义中间件

```go
// server/middleware.go
package server

import (
    "context"
    "time"

    "github.com/mark3labs/mcp-go/mcp"
    mcpserver "github.com/mark3labs/mcp-go/server"
    log "github.com/sirupsen/logrus"
)

// TimingMiddleware 记录每个 tool 调用的耗时
type TimingMiddleware struct{}

func (m *TimingMiddleware) Process(
    next mcpserver.ToolHandlerFunc,
) mcpserver.ToolHandlerFunc {
    return func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
        start := time.Now()
        result, err := next(ctx, req)
        log.Infof("tool %s took %v", req.Params.Name, time.Since(start))
        return result, err
    }
}

// AuthMiddleware 从 context 校验认证信息
type AuthMiddleware struct{}

func (m *AuthMiddleware) Process(
    next mcpserver.ToolHandlerFunc,
) mcpserver.ToolHandlerFunc {
    return func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
        if ctx.Value(userKey) == nil {
            return mcp.NewToolResultError("unauthorized"), nil
        }
        return next(ctx, req)
    }
}
```

### 注册中间件

```go
// server/server.go
func New() *mcpserver.MCPServer {
    s := mcpserver.NewMCPServer("my-mcp-server", "1.0.0",
        mcpserver.WithRecovery(),
        mcpserver.WithToolCapabilities(true),
    )

    // 中间件按注册顺序执行，最先注册的最先执行
    s.Use(&TimingMiddleware{}, &AuthMiddleware{})

    tools.Register(s)
    return s
}
```

---

## 认证与请求上下文

使用 `WithHTTPContextFunc` 从请求头提取认证信息，注入到 `context.Context`，供中间件和 handler 使用。

```go
// server/context.go
package server

import (
    "context"
    "net/http"
)

type contextKey string

const userKey contextKey = "user"

// httpContextFunc 从请求头提取用户信息注入 context
func httpContextFunc(ctx context.Context, r *http.Request) context.Context {
    token := r.Header.Get("Authorization")
    user := validateToken(token) // 自行实现 token 校验
    return context.WithValue(ctx, userKey, user)
}
```

```go
// main.go 中挂载
httpServer := mcpserver.NewStreamableHTTPServer(s,
    mcpserver.WithEndpointPath("/mcp"),
    mcpserver.WithStateLess(true),
    mcpserver.WithHTTPContextFunc(httpContextFunc),
)
```

---

## 模板与参考

本 skill 目录包含可直接使用的代码模板和安全参考：

| 文件 | 用途 |
|------|------|
| `templates/main.go` | 最小可运行的 MCP server 入口 |
| `templates/tool.go` | 标准 tool handler 骨架（含日志、参数提取、错误处理） |
| `templates/middleware.go` | 中间件骨架（Timing、Logging、Recovery 示例） |
| `templates/Dockerfile` | 多阶段构建容器化模板 |
| `references/security-checklist.md` | 网络类 MCP 五阶段安全检查清单 |

新建项目时，复制 `templates/` 下的文件作为起点，替换占位符为实际代码。

---

## 构建与验证

开发完成后必须执行：

```bash
gofmt -w .
go build ./...
```

两条命令均通过后再提交。构建产物（二进制文件）提交前删除。

---

## 常见模式

### 返回结构化内容

```go
// 返回纯文本
return mcp.NewToolResultText("some text"), nil

// 返回多段内容
return &mcp.CallToolResult{
    Content: []mcp.Content{
        mcp.TextContent{Type: "text", Text: "result:"},
        mcp.TextContent{Type: "text", Text: jsonStr},
    },
}, nil
```

### 工具分页

当数据量大时，在 Tool 中加 `page`/`page_size` 参数，由 handler 自行分页返回，不依赖 SDK 内置机制。

### 并发安全

`MCPServer` 实例是并发安全的，所有 `AddTool`/`AddResource`/`AddPrompt` 应在 server 启动前完成注册，启动后不再修改。

---

## 实战经验：开发网络类 MCP Server 的教训

以下内容基于 fetch-mcp（网页抓取 MCP server）的实际开发过程总结。

### 安全边界：必须由人工决策的事项

MCP server 通常由 LLM 自主调用，但以下安全策略 **不能由 AI 自行决定**，必须由开发者明确指定：

| 决策项 | 说明 | 默认建议 |
|--------|------|---------|
| 响应体体积上限 | 防止目标服务器返回超大内容导致 OOM | 10MB |
| URL 长度限制 | 防止缓冲区攻击 | 2000 字符 |
| 跨域重定向策略 | 跟随、拦截还是返回元数据让 LLM 决策 | 拦截跨域重定向 |
| SSRF 防护范围 | 哪些内网地址段需要拦截 | 127/10/172.16/192.168/169.254 |
| http→https 升级 | 是否强制加密 | 强制升级 |
| URL 凭据剥离 | 是否清除 `user:pass@host` | 强制剥离 |
| LLM 沙盒隔离 | 是否用子模型摘要外部内容（取决于信任边界） | 自建服务可跳过 |

### 外部内容摄入的防护层清单

任何涉及抓取、读取外部数据的 MCP tool，应按以下清单逐项检查：

```
阶段 1: URL 验证
  □ 长度限制
  □ http→https 升级
  □ 认证凭据剥离（user:pass@）
  □ 已知 URL 规范化（如 GitHub blob→raw）

阶段 2: 域名安全
  □ 白名单/黑名单过滤
  □ 恶意域名检查（钓鱼、恶意软件）
  □ （可选）云端域名验证 API

阶段 3: 网络请求
  □ 响应体体积上限（io.LimitReader）
  □ 跨域重定向拦截（CheckRedirect）
  □ 内网地址拦截（SSRF 防护）
  □ 超时设置（连接、TLS、响应头）
  □ 本地缓存（减少重复请求）

阶段 4: 内容处理
  □ 压缩解压（gzip/deflate/br）
  □ HTML→Markdown 转换策略
  □ 内容截断保护 + 警告标记

阶段 5: 输出净化（可选，取决于信任边界）
  □ LLM 沙盒摘要（防止提示词注入）
  □ 引用长度限制
  □ 版权合规检查
```

### 缓存设计要点

- **TTL 建议**：15 分钟（平衡新鲜度与性能）
- **键**：规范化后的 URL
- **并发安全**：必须用 `sync.RWMutex` 保护
- **缓存失效**：不需要主动失效，TTL 自然过期即可
- **注入方式**：通过 Config 结构体传入 handler，不要在 handler 内部创建

```go
// fetcher/cache.go
type Cache struct {
    mu      sync.RWMutex
    entries map[string]cacheEntry
}

func (c *Cache) Get(url string) (*Result, bool) { ... }
func (c *Cache) Set(url string, result *Result) { ... }
```

### API 签名变更的连锁反应

修改底层函数签名时，**必须全局搜索所有调用方**，遗漏会导致编译失败。

例如 `NormalizeURL` 从 `func(string) string` 改为 `func(string) (string, error)` 后：
- `tools/fetch.go` 中的调用需要处理 error
- `prompts/fetch.go` 中的调用同样需要处理 error
- 任何新增的调用方都必须同步更新

**规则**：修改被多个包调用的函数签名前，先用 `grep -rn "NormalizeURL"` 找出所有调用点，逐一更新。

### gopls 工作区误报

当项目不在 VS Code 工作区时，gopls 会报大量 `could not import` 和 `undefined` 错误。这些是 LSP 配置问题，**不影响 `go build`**。判断标准：

- `go build ./...` 通过 = 代码正确
- gopls 报 import 错误 = 工作区配置问题，可忽略

### HTML 处理策略选择

`go-readability` 对文章类页面（博客、新闻）效果很好，但对 API 文档、表格页面会过度提取导致内容丢失。

**建议**：提供 `mode` 参数让 LLM 自行选择：
- `article`：readability 提取正文（默认）
- `full`：全量 HTML→Markdown，保留页面结构

### 中间件 vs 手动注入

mark3labs/mcp-go 的中间件系统（`s.Use()`）适用于横切逻辑（日志、鉴权）。但像缓存、域名过滤这类 **tool 专属配置**，更适合通过 Config 结构体注入，而非中间件。原因：
- 中间件对所有 tool 生效，但某些逻辑只属于特定 tool
- Config 注入更灵活，可以在 handler 内部精确控制使用时机
