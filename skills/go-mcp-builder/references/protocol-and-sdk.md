# Protocol and SDK Selection

MCP and its SDKs change independently. Verify both before choosing APIs or wire
behavior.

## Official Sources

Use primary sources in this order:

1. Current dated specification: <https://modelcontextprotocol.io/specification>
2. Specification repository and changelog:
   <https://github.com/modelcontextprotocol/modelcontextprotocol>
3. Official Go SDK releases:
   <https://github.com/modelcontextprotocol/go-sdk/releases>
4. Official Go SDK compatibility table and docs:
   <https://github.com/modelcontextprotocol/go-sdk>
5. Go package API for the selected tag:
   <https://pkg.go.dev/github.com/modelcontextprotocol/go-sdk>

Record the verification date, exact protocol revision, exact SDK tag, supported
Go version, and required capabilities in the task. Prefer the newest stable SDK
that declares full support for the selected dated protocol. Do not select a
pre-release merely because it has a larger version number.

## Verified Baseline

The following is a reproducible baseline, not a permanent "latest" claim:

| Item | Verified value |
| --- | --- |
| Verification date | 2026-09-04 |
| Dated MCP revision | `2026-07-28` |
| Official Go SDK | `github.com/modelcontextprotocol/go-sdk v1.7.0` |
| SDK Go directive | Go 1.25 |
| Previous compatibility revision | `2025-11-25` |

Before implementation, repeat the official-source check. If a newer stable SDK
exists, read its release notes and capability table before changing the pin.

## `2026-07-28` Lifecycle

- The protocol is stateless: there is no `initialize` /
  `notifications/initialized` handshake.
- `server/discover` reports server identity, capabilities, and supported
  versions before ordinary requests.
- Each request carries protocol version and client capabilities in
  `_meta.io.modelcontextprotocol/*`.
- Streamable HTTP uses one POST per request. A response is JSON or a
  request-scoped SSE stream.
- Standalone GET streams, protocol-level sessions, `Mcp-Session-Id`, and
  `Last-Event-ID` resumability are not part of this revision.
- Server-initiated calls use multi-round-trip results. Roots, Sampling, and MCP
  Logging are deprecated; do not introduce them in a new server without an
  identified compatibility requirement.

The official Go SDK requires `StreamableHTTPOptions.Stateless=true` for this
revision and implements `server/discover`, request metadata, header/body
validation, and version negotiation.

Tag-level check: `v1.7.0` does not yet expose the main-branch
`ServerOptions.SupportedProtocolVersions` field. It advertises the SDK's built-in
version matrix. A product that must narrow the advertised or accepted set needs
an application protocol guard plus response middleware, with direct tests. Do
not use a main-branch field in code pinned to `v1.7.0`.

## Compatibility Policy

- Advertise and accept only revisions required by real clients when the selected
  SDK tag exposes that control. Otherwise add a tested application guard or
  document the wider SDK matrix explicitly.
- Test each advertised revision using its own lifecycle. A passing latest-version
  test does not prove a legacy handshake works.
- Do not restore the deprecated HTTP+SSE transport for a new server.
- Keep SDK compatibility switches such as `MCPGODEBUG` out of persistent
  configuration unless a reproduced dependency requires a bounded transition.
