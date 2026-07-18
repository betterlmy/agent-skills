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

// LoggingMiddleware 记录 tool 调用的入参和出参摘要
type LoggingMiddleware struct{}

func (m *LoggingMiddleware) Process(
	next mcpserver.ToolHandlerFunc,
) mcpserver.ToolHandlerFunc {
	return func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		log.Infof(">>> tool %s called", req.Params.Name)
		result, err := next(ctx, req)
		if err != nil {
			log.Infof("<<< tool %s returned error: %v", req.Params.Name, err)
		} else {
			log.Infof("<<< tool %s returned success", req.Params.Name)
		}
		return result, err
	}
}

// RecoveryMiddleware 示例：自定义 panic 恢复逻辑（SDK 已内置 WithRecovery，此为例）
type RecoveryMiddleware struct{}

func (m *RecoveryMiddleware) Process(
	next mcpserver.ToolHandlerFunc,
) mcpserver.ToolHandlerFunc {
	return func(ctx context.Context, req mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		defer func() {
			if r := recover(); r != nil {
				log.Errorf("tool %s panicked: %v", req.Params.Name, r)
			}
		}()
		return next(ctx, req)
	}
}
