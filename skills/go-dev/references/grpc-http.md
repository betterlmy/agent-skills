# gRPC 与 HTTP API 规范

## gRPC 接口规范

所有 gRPC 服务方法必须遵循以下模板：

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

    // 业务逻辑实现

    return resp, nil
}
```

关键要点：

- `=== MethodName in/out ===` 标记方法执行边界。
- `log.Infof("request: %+v", req)` 记录请求参数；敏感字段必须先脱敏。
- 响应初始化时设置默认成功状态码。
- 使用 `defer` 确保方法结束时记录响应和结束标记。
- 错误时修改 `resp.Code` 和 `resp.Message`，而非直接返回 `error`。

错误处理示例：

```go
if err != nil {
    log.Errorf("MethodName error: %v", err)
    resp.Code = int32(codes.Internal)
    resp.Message = codes.Internal.Message()
    return resp, nil
}
```

## HTTP 状态码统一 200

所有普通 JSON HTTP API 必须统一返回 HTTP `200 OK`，业务成功或失败都通过响应体里的 `code` 和 `message` 表达。

强制要求：

- Handler 中不要用 HTTP `400/401/403/404/500` 表达业务错误；参数错误、鉴权失败、数据不存在、内部错误都写入响应体 `code` 和 `message`。
- Swagger 注释统一写 `@Success 200 {object} ResponseType "响应"`，不要为业务错误额外声明 `@Failure 4xx/5xx`。
- 推荐使用 `defer` 做统一出口，避免多个分支重复 `c.JSON`。
- 如果项目已有 `apis.Result`、`apis.Errors`、`apis.ResultWithMes` 等封装，必须优先复用；这些封装内部也必须 `c.JSON(http.StatusOK, ...)`。
- 文件下载、重定向、静态资源、健康探针、纯中间件协议拦截等非 JSON 业务 API 可按协议需要使用其他 HTTP 状态码。

统一响应格式：

```go
type Response struct {
    Code    int32       `json:"code"`
    Message string      `json:"message"`
    Data    interface{} `json:"data"`
}
```

## 统一响应封装

普通 JSON HTTP API 优先使用项目已有的统一出口风格：函数入口打印 `=== Xxx in ===`，预初始化 `apiResp`，使用 `defer` 统一记录响应、打印 `=== Xxx out ===` 并 `c.JSON(http.StatusOK, apiResp)`，后续分支只修改 `apiResp.Code`、`apiResp.Message`、`apiResp.Data` 后 `return`。

Handler 日志要求：

- 入口第一行打印 `log.Infof("=== Xxx in ===")`。
- 出口通过 `defer` 打印 `log.Infof("resp: %+v", apiResp)` 和 `log.Infof("=== Xxx out ===")`。
- 请求参数绑定成功后打印 `log.Infof("request: %+v", apiReq)`；GET/query/path 参数同理在绑定或解析成功后打印。
- 如果请求或响应包含 token、cookie、password、secret、Authorization、access_token、refresh_token、身份证号、手机号等敏感信息，禁止完整打印，必须脱敏后打印摘要或跳过该字段。
- SSE、文件下载、重定向、静态资源等协议特例仍需按协议返回，不强行套普通 JSON handler 模板。

响应工具示例：

```go
package response

import (
    "net/http"

    "github.com/gin-gonic/gin"

    "project/internal/codes"
)

type Response struct {
    Code    codes.Code `json:"code"`
    Message string     `json:"message"`
    Data    any        `json:"data"`
}

func New() *Response {
    return &Response{
        Code:    codes.OK,
        Message: codes.Message(codes.OK),
    }
}

func (r *Response) SetError(code codes.Code) {
    r.Code = code
    r.Message = codes.Message(code)
    r.Data = nil
}

func (r *Response) SetErrorWithMsg(code codes.Code, msg string) {
    r.Code = code
    r.Message = msg
    r.Data = nil
}

func JSON(c *gin.Context, resp *Response) {
    c.JSON(http.StatusOK, resp)
}
```

## 普通 JSON Handler 模板

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

强类型响应结构体场景：

```go
func Xxx(c *gin.Context) {
    log.Infof("=== Xxx in ===")

    apiResp := &ApiXxxResponse{
        Code:    uint32(codes.OK),
        Message: codes.Message(codes.OK),
    }
    defer func() {
        log.Infof("resp: %+v", apiResp)
        log.Infof("=== Xxx out ===")
        c.JSON(http.StatusOK, apiResp)
    }()

    var apiReq ApiXxxRequest
    if err := c.ShouldBindJSON(&apiReq); err != nil {
        apiResp.Code = uint32(codes.BadRequest)
        apiResp.Message = codes.Message(codes.BadRequest)
        log.Errorf("Xxx ShouldBindJSON error. err[%v]", err)
        return
    }
    log.Infof("request: %+v", apiReq)

    // 业务逻辑只修改 apiResp
}
```

## List 接口规范

所有 List 接口必须初始化 Data 和 RecordList，确保返回空数组而不是 nil：

```go
resp := &ApiListXxxResponse{
    Code:    int32(codes.OK),
    Message: codes.Message(codes.OK),
    Data: &ApiListXxxData{
        RecordList: []*ApiGetXxxData{},
    },
}
```

## Request/Response 命名规范

- Request: `Api{Action}{Entity}Request`
- Response: `Api{Action}{Entity}Response` + `Api{Action}{Entity}Data`
- 转换函数: `ConvertTo{Target}`
