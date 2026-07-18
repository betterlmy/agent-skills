---
name: go-dev
description: Go 开发规范技能，覆盖命名、注释、日志、配置加载、gRPC、Gin HTTP API、GORM Model、DAO、SQL 和数据库约束。Use when writing, reviewing, or refactoring Go code, gRPC services, HTTP handlers, API response contracts, database models, SQL migrations, or project coding conventions.
when_to_use: "编写Go代码、gRPC服务、HTTP API、Gin handler、数据库Model、GORM结构体、SQL、配置加载、日志规范、编码规范查询、命名规范查询"
---

# Go Dev

## 使用方式

开始编写或审查 Go 代码前，先按任务类型读取最小必要参考：

- 基础 Go 规范、命名、注释、配置和日志：读 `references/core-go.md`
- gRPC、HTTP API、Gin handler、响应体、Swagger 和 in/out 日志：读 `references/grpc-http.md`
- GORM Model、DAO、错误处理、SQL 建表和索引：读 `references/gorm-database.md`
- 完整 SQL 细则：必要时读 `sql-standards.md`
- 示例代码：需要模板时读 `examples/grpc_service.go`、`examples/http_handler.go`、`examples/model_example.go`

## 全局硬规则

- 对话、文档和代码说明使用中文；Markdown 文档保持中文标题和中文说明。
- 优先沿用当前仓库已有封装、包名和风格，不新增第二套日志、响应或 DAO 体系。
- `.env` 只用于本地和部署注入，不提交真实 token、secret、cookie，也不在日志中打印敏感配置。
- 业务代码、handler、service、DAO 不直接使用标准库 `log`、`log/slog` 或 logrus；使用项目已有 `log` 封装。
- 日志禁止完整打印 token、cookie、password、secret、Authorization、access_token、refresh_token、身份证号、手机号等敏感信息。
- I/O、RPC、数据库、外部 API 调用要接收并传递 `context.Context`；长耗时操作要考虑超时或取消。

## 命名速查

| 类型 | 规范 | 示例 |
| --- | --- | --- |
| 文件名 | 下划线分隔 | `device_api.go` |
| 结构体 | 大驼峰 | `AccountRecord` |
| 导出函数 | 大驼峰 | `GenerateAccessToken` |
| 私有函数 | 小驼峰 | `getTenantId` |
| 全局变量 | 大驼峰 | `Conf`、`Db`、`Rdb` |
| 局部变量 | 小驼峰 | `tenantId` |
| 常量 | 全大写下划线 | `ACCESS_TOKEN_EXPIRE_TIME` |

## 日志速查

- gRPC 方法入口：`log.Infof("=== MethodName in ===")`
- gRPC 请求：`log.Infof("request: %+v", req)`，敏感字段先脱敏
- gRPC 出口：`log.Infof("resp: %+v", resp)` + `log.Infof("=== MethodName out ===")`
- HTTP Handler 入口：`log.Infof("=== HandlerName in ===")`
- HTTP Handler 请求：绑定成功后打印脱敏后的 `apiReq`
- HTTP Handler 出口：统一 `defer` 打印响应和 `log.Infof("=== HandlerName out ===")`
- 业务错误：`log.Errorf(...)` 后修改业务响应或返回错误，不直接泄露密钥和凭证。

## gRPC 必守模板

```go
func (s *Service) MethodName(ctx context.Context, req *pb.MethodRequest) (*pb.MethodResponse, error) {
    log.Infof("=== MethodName in ===")
    log.Infof("request: %+v", req)

    resp := &pb.MethodResponse{
        Code:    int32(codes.OK),
        Message: codes.Message(codes.OK),
    }

    defer func() {
        log.Infof("resp: %+v", resp)
        log.Infof("=== MethodName out ===")
    }()

    return resp, nil
}
```

错误分支修改 `resp.Code` 和 `resp.Message` 后 `return resp, nil`；不要把业务错误直接作为 gRPC `error` 返回。

## HTTP Handler 必守模板

普通 JSON HTTP API 统一 HTTP `200 OK`，业务状态通过 `{code,message,data}` 表达。Handler 使用入口日志、预初始化响应、`defer` 统一出口，分支只修改响应体。

```go
func Xxx(c *gin.Context) {
    log.Infof("=== Xxx in ===")

    apiResp := response.New()
    defer func() {
        log.Infof("resp: %+v", apiResp)
        log.Infof("=== Xxx out ===")
        response.JSON(c, apiResp)
    }()

    var apiReq ApiXxxRequest
    if err := c.ShouldBindJSON(&apiReq); err != nil {
        apiResp.SetError(codes.BadRequest)
        log.Errorf("Xxx ShouldBindJSON error. err[%v]", err)
        return
    }
    log.Infof("request: %+v", apiReq)

    data, err := service.Xxx(c.Request.Context(), &apiReq)
    if err != nil {
        apiResp.SetErrorWithMsg(codes.InternalServerError, err.Error())
        return
    }
    apiResp.Data = data
}
```

SSE、CSV、文件下载、重定向、静态资源、健康探针等协议特例不强行套普通 JSON 模板。

## 数据库速查

- Model 时间字段用应用层和数据库层双重保险：`autoCreateTime` / `autoUpdateTime` + `default:CURRENT_TIMESTAMP(3)`。
- json 标签使用 snake_case；线上字段名不同则用 `gorm:"column:..."` 映射。
- DAO 查询使用 `Db.Debug().WithContext(ctx)`，并手动加 `Where("is_deleted = 0")`。
- 所有表优先使用 `t_` 前缀；线上已存在表名保持原名。
- 基础字段包含 `id`、`create_time`、`create_user`、`update_time`、`update_user`、`is_deleted`。
- 表级声明使用 `ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin`。
- 普通索引 `idx_`，唯一索引 `uk_`，使用 `KEY` 关键字。
- 所有字段和表添加中文 `COMMENT`；数据库名用 `${DBNAME}` 占位，不硬编码。

## 修改后检查

- 修改 Go 代码后运行当前仓库要求的 Go 检查，通常至少 `go test ./...` 或项目 Makefile 中的测试命令。
- 修改 HTTP API、Swagger、响应结构或前端生成类型时，同步更新 DTO、Swagger 注释和生成代码。
- 修改 SQL、Model 或 DAO 时，对照 `references/gorm-database.md` 和 `sql-standards.md` 检查字段、索引、软删除和时间精度。
