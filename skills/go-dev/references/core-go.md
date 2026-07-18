# Go 基础规范

## 命名规范

| 类型 | 风格 | 示例 |
| --- | --- | --- |
| 文件名 | 下划线分隔 | `device_api.go`, `mysql_model.go` |
| 结构体 | 大驼峰 | `AccountRecord`, `ApiJobAddRequest` |
| 导出函数 | 大驼峰 | `GenerateAccessToken()`, `PropertySet()` |
| 私有函数 | 小驼峰 | `getTenantId()`, `getJWTClaimsFromUser()` |
| 全局变量 | 大驼峰 | `Conf`, `Db`, `Rdb` |
| 局部变量 | 小驼峰 | `tenantId`, `isDeleted` |
| 常量 | 全大写下划线分隔 | `ACCESS_TOKEN_EXPIRE_TIME`, `CONTACT_TYPE_EMAIL` |

## 注释规范

导出函数、导出变量和导出常量必须有注释，注释以标识符名开头。

```go
// FunctionName 功能描述
func FunctionName() {}

// ErrConfigNotFound 定价配置未找到
var ErrConfigNotFound = errors.New("config not found")
```

HTTP API 必须写 Swagger 注释：

```go
// @Summary 接口摘要
// @Tags 模块标签
// @Security BasicAuth
// @Param request body RequestType true "请求body"
// @Success 200 {object} ResponseType "响应"
// @Router /api/v1/path [post]
```

## 配置加载规范

- `.env` 读取统一使用 `github.com/joho/godotenv`；禁止手写 `os.Open` + `bufio.Scanner` 的 dotenv 解析器。
- API 入口推荐使用 blank import 自动加载：

```go
import (
    _ "github.com/joho/godotenv/autoload"
)
```

- 如果需要显式控制加载顺序，在 `main` 开始处调用 `godotenv.Load()`，再执行 `config.Load()`。
- `.env` 只用于本地和部署环境注入，不要提交真实 token、secret、cookie；日志中禁止打印敏感配置值。

## 日志规范

- 日志底层使用基于 `go.uber.org/zap` 改造的统一日志包，不直接在业务代码里裸用 `go.uber.org/zap`。
- 业务代码统一使用当前项目已有的 `log` 封装包；具体 import 路径以当前仓库为准，不在业务代码里新增另一套日志体系。
- 业务代码、启动代码、handler、service、DAO 不直接使用标准库 `log`、`log/slog` 或 logrus；GORM 等第三方适配例外见下方。
- 默认使用 `log.Infof`、`log.Errorf`、`log.Warnf`、`log.Fatalf` 等格式化接口，保持项目现有风格。
- 需要结构化日志时使用封装包提供的 `log.InfoW`、`log.ErrorW`、`log.WarnW`，字段按 key-value 成对传入。
- 启动失败使用 `log.Fatalf("message:%v", err)`；普通业务错误使用 `log.Errorf(...)` 后按业务响应或错误返回处理。
- 只有第三方库接口强制要求 `Printf` 风格 writer 时，才用小 adapter 转发到统一日志包。

import 示例：

```go
import "gitlab-esd.leapmotor.com/psa/product/lp-go-tool.git/log"
```

## 其他约定

- 导入顺序：标准库、第三方库、本项目。
- 使用 `context.Context` 传递上下文，不要忽略已有 context 参数。
- 长时间操作需检查 `ctx.Done()` 响应取消信号，子操作按场景使用 `context.WithTimeout` 设置超时。
