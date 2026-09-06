package main

import (
	"errors"
	"log/slog"
	"net/http"
	"os"
	"time"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stderr, nil))
	server := mcp.NewServer(
		&mcp.Implementation{Name: "example-go-mcp-server", Version: "0.1.0"},
		&mcp.ServerOptions{Capabilities: &mcp.ServerCapabilities{}, Logger: logger},
	)
	mcp.AddTool(server, &mcp.Tool{
		Name:        "greet",
		Description: "Return a greeting for the supplied name.",
	}, greet)

	mcpHandler := mcp.NewStreamableHTTPHandler(
		func(*http.Request) *mcp.Server { return server },
		&mcp.StreamableHTTPOptions{
			Stateless:                    true,
			JSONResponse:                 true,
			Logger:                       logger,
			MaxRequestBodyBytes:          1 << 20,
			PropagateRequestCancellation: true,
		},
	)
	originProtection := http.NewCrossOriginProtection()
	mux := http.NewServeMux()
	mux.Handle("/mcp", accessLog(logger, originProtection.Handler(mcpHandler)))

	httpServer := &http.Server{
		Addr:              "127.0.0.1:8080",
		Handler:           mux,
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       30 * time.Second,
		WriteTimeout:      30 * time.Second,
	}
	logger.Info("MCP server listening", "addr", httpServer.Addr)
	if err := httpServer.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		logger.Error("MCP server stopped", "error_class", "http_server")
		os.Exit(1)
	}
}
