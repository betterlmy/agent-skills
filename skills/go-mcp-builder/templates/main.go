package main

import (
	"flag"
	"log"

	"my-mcp-server/server"
)

func main() {
	port := flag.Int("port", 8080, "HTTP listen port")
	flag.Parse()

	handler, err := server.New(server.Config{})
	if err != nil {
		log.Fatalf("failed to create server: %v", err)
	}

	addr := server.Addr(*port)
	log.Printf("MCP server listening on %s", addr)
	if err := server.ListenAndServe(addr, handler); err != nil {
		log.Fatalf("server error: %v", err)
	}
}
