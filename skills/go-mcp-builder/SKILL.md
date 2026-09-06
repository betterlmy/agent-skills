---
metadata:
  external-cli: "true"
  cli-compatibility: "references/cli-compatibility.md"
name: go-mcp-builder
description: Build, extend, review, or debug Go MCP servers against current official Model Context Protocol specifications and the official Go SDK. Use when a task adds MCP tools, resources, prompts, Streamable HTTP or stdio transport, MCP authentication, protocol-version compatibility, conformance checks, or an MCP endpoint to an existing Go service.
---

# Go MCP Server Builder

## Goal

Build the smallest secure MCP surface that fits the host repository. Treat the
repository's instructions and architecture as authoritative, and treat MCP
specification and SDK details as version-sensitive facts that must be checked
against official sources before implementation.

## Start Here

1. Inspect repository instructions, Go version, module boundaries, HTTP stack,
   authentication, logging, tests, and existing business use cases.
2. Read [protocol-and-sdk.md](references/protocol-and-sdk.md), verify the latest
   dated MCP specification and official Go SDK release, then pin the selected
   versions in the task. Do not copy an SDK choice from an old example.
3. Classify each requested capability with
   [server-design.md](references/server-design.md): Tool, Resource, Prompt, or
   no MCP surface. Do not expose every existing REST operation mechanically.
4. For Streamable HTTP, authentication, external content, or sensitive data,
   read [security-and-auth.md](references/security-and-auth.md) before coding.
5. If conformance tooling is needed, read the bundled
   [CLI compatibility contract](references/cli-compatibility.md) before running
   it. Installing or downloading tools still requires the task's authorization.

## Implementation Workflow

1. Define the public contract first: server identity, supported protocol
   versions, transport, capability names, JSON Schemas, structured results,
   authorization requirements, error semantics, and compatibility window.
2. Reuse existing application services through narrow adapters. Keep MCP
   decoding, authentication context, and result mapping out of domain logic.
3. Prefer the official `github.com/modelcontextprotocol/go-sdk`. If a repository
   already locks another SDK, verify that SDK's current protocol support before
   deciding whether migration belongs in scope.
4. Use typed Tool inputs and outputs with `mcp.AddTool`; provide explicit input
   and output schemas when inference cannot express bounds or strict unknown
   field rejection. Return both structured content and an equivalent text block
   when older clients are supported.
5. Propagate request Context through database, network, and provider calls.
   Bound request bodies, work, concurrency, output size, and time.
6. Keep transport errors, JSON-RPC protocol errors, and recoverable Tool
   execution errors distinct. Public errors must be stable and sanitized.
7. Log only allowlisted metadata such as request ID, method or Tool name,
   outcome, and duration. Never log complete arguments, results, headers,
   prompts, credentials, or fetched content.
8. Update public documentation and deployment routing when adding a network
   endpoint. OpenAPI does not describe an MCP JSON-RPC endpoint unless the host
   repository has an explicit convention for doing so.

## Transport Defaults

- New remote servers use Streamable HTTP at `/mcp`; new local subprocess tools
  use stdio when that better matches the client lifecycle.
- For MCP `2026-07-28`, use a stateless Streamable HTTP handler. Do not add the
  removed standalone GET stream, protocol sessions, or `Last-Event-ID` paths.
- Enable request cancellation, Origin protection, DNS-rebinding protection, and
  an explicit body limit. Bind local-only examples to loopback.
- Preserve older revisions only when required by identified clients and verify
  each revision independently.

## Validation

1. Add tests for schema validation, structured output, business-error mapping,
   cancellation, authentication and authorization, body limits, Origin/Host
   checks, and every claimed protocol revision.
2. Use an official SDK client for end-to-end discovery, feature listing, and
   invocation. Do not treat compilation as protocol validation.
3. Run the repository's format, test, race, vet, build, and generated-contract
   checks that match the change.
4. For reusable templates, run `bash scripts/verify-templates.sh`; it copies the
   template to a temporary directory before downloading modules or building.
5. Use the official conformance runner as a supplementary check when its
   scenarios match the product server. Record unsupported optional capabilities
   as out of scope, not as passing.

## Bundled Resources

- [protocol-and-sdk.md](references/protocol-and-sdk.md): current-source and
  version-negotiation workflow.
- [server-design.md](references/server-design.md): capability, schema, result,
  error, transport, and integration design.
- [security-and-auth.md](references/security-and-auth.md): HTTP authorization,
  cross-origin, logging, rate-limit, and untrusted-content boundaries.
- `templates/`: minimal, loopback-only official SDK server.
- `evals/prompts.md`: trigger and forward-evaluation cases.

This Skill does not replace repository-specific Go, security, deployment, or
product rules, and it does not apply to generic Go HTTP work that has no MCP
contract.
