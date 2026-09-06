# MCP Server Design

## Choose the Capability

| Need | MCP surface |
| --- | --- |
| Model decides when to query, compute, or mutate | Tool |
| Application or user selects addressable context | Resource or Resource Template |
| User chooses a reusable message workflow | Prompt |
| Long-running operation needs a durable handle | Task extension, only when the client supports it |

Start with the smallest surface. A REST API with twenty operations does not
need twenty MCP Tools. Prefer one task-oriented Tool over a transport-shaped
wrapper when it preserves the product's authorization and business semantics.

## Tools

- Use stable, unique names of 1-128 characters from ASCII letters, digits,
  underscore, hyphen, and dot.
- Write descriptions for model selection: state what the Tool does, required
  context, side effects, and important limits.
- Use typed inputs and outputs with `mcp.AddTool`. Override inferred schemas when
  bounds, enums, `additionalProperties: false`, or compatibility require it.
- Define an output schema and return structured content. When supporting older
  clients, include the same JSON serialized into `TextContent`.
- Do not put secrets, personal information, queries, or free-form content in
  `x-mcp-header`; those values are visible to intermediaries.

## Errors

- Malformed JSON-RPC, unsupported methods, invalid protocol metadata, and
  unexpected server failures are protocol errors.
- Invalid domain input, resource conflicts, unavailable upstream operations,
  and other errors an LLM can correct are Tool results with `isError=true`.
- Authentication and authorization failures belong to the HTTP authorization
  boundary for Streamable HTTP.
- Map internal errors to stable public messages. Preserve the underlying error
  only in a controlled server log.

## HTTP Integration

`mcp.NewStreamableHTTPHandler` is an `http.Handler`. In an existing service,
mount it under an outer `http.ServeMux` or the framework's native `http.Handler`
adapter. Keep MCP responses out of a REST response envelope and make sure panic
recovery does not write two incompatible protocols.

Recommended `2026-07-28` options:

```go
&mcp.StreamableHTTPOptions{
    Stateless:                    true,
    JSONResponse:                 true, // when progress/SSE is not needed
    MaxRequestBodyBytes:          1 << 20,
    PropagateRequestCancellation: true,
}
```

Use `http.NewCrossOriginProtection().Handler(handler)` around the MCP handler.
Leave the SDK's localhost protection enabled. Use explicit trusted origins only
for known browser clients.

For authenticated results, set MCP cache scope to private and avoid shared HTTP
caching. Do not add resource subscriptions or EventStore state to a stateless
server that exposes only fixed Tools.

## Testing

Cover:

- discovery and version negotiation;
- deterministic feature lists;
- strict input and output schemas;
- success, recoverable Tool failure, and internal failure;
- empty collections as `[]` rather than `null` when the contract requires it;
- cancellation and deadlines;
- every authentication and Scope branch;
- protocol headers, Content-Type, Accept, body size, methods, Origin, and Host;
- sensitive-value absence from logs and errors.
