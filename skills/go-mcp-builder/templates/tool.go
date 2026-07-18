package tools

import (
	"context"
	"fmt"

	"github.com/mark3labs/mcp-go/mcp"
	log "github.com/sirupsen/logrus"
)

// registerExampleTools 注册示例 tool
func registerExampleTools(s *mcpserver.MCPServer) {
	exampleTool := mcp.NewTool("example",
		mcp.WithDescription("示例 tool，替换为实际功能描述"),
		mcp.WithString("param",
			mcp.Required(),
			mcp.Description("参数说明"),
		),
		mcp.WithNumber("limit",
			mcp.Description("可选参数说明，默认 0"),
		),
		mcp.WithBoolean("verbose",
			mcp.Description("是否输出详细信息，默认 false"),
		),
	)
	s.AddTool(exampleTool, handleExample)
}

func handleExample(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
	log.Infof("=== handleExample in ===")
	log.Infof("request: %+v", req)

	param, err := req.RequireString("param")
	if err != nil {
		log.Infof("=== handleExample out === error: %v", err)
		return mcp.NewToolResultError(err.Error()), nil
	}

	limit := req.GetInt("limit", 0)
	verbose := req.GetBool("verbose", false)

	// 业务逻辑...
	result := fmt.Sprintf("processed %s with limit=%d verbose=%v", param, limit, verbose)

	log.Infof("=== handleExample out === resultLen=%d", len(result))
	return mcp.NewToolResultText(result), nil
}
