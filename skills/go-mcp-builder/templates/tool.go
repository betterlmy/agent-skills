package main

import (
	"context"
	"strings"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

type greetInput struct {
	Name string `json:"name" jsonschema:"name to greet"`
}

type greetOutput struct {
	Greeting string `json:"greeting" jsonschema:"generated greeting"`
}

func greet(_ context.Context, _ *mcp.CallToolRequest, input greetInput) (*mcp.CallToolResult, greetOutput, error) {
	name := strings.TrimSpace(input.Name)
	if name == "" {
		return &mcp.CallToolResult{
			Content: []mcp.Content{&mcp.TextContent{Text: "name must not be empty"}},
			IsError: true,
		}, greetOutput{}, nil
	}
	return nil, greetOutput{Greeting: "Hello, " + name + "!"}, nil
}
