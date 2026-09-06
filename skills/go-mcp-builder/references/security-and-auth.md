# Security and Authorization

## Trust Boundary

An MCP Tool is model-invoked but still crosses an ordinary application security
boundary. Derive tenant and user identity only from verified credentials, apply
authorization on every request, and re-check ownership for every opaque handle.
Tool descriptions and annotations are untrusted metadata from a client's point
of view and do not enforce policy.

## Streamable HTTP

- Require TLS outside loopback. If TLS terminates at a gateway, restrict direct
  backend reachability and document trusted proxy behavior.
- Validate `Origin` on every browser-originated request. Keep DNS-rebinding and
  Host protection enabled.
- Bound request bodies before decoding and bound result size before returning.
- Accept credentials only in `Authorization: Bearer ...`; never in query strings.
- Forward `Mcp-Protocol-Version`, `Mcp-Method`, `Mcp-Name`, and supported
  `Mcp-Param-*` headers unchanged through gateways. The handler must reject
  header/body mismatches.
- Rate limit after authentication when the limit is tenant- or user-scoped.

## Authorization Choices

For public third-party HTTP interoperability, implement the MCP authorization
profile: OAuth 2.1, Protected Resource Metadata, authorization-server discovery,
resource indicators and audience validation, PKCE, and least-privilege Scope
challenges.

For a controlled internal client, a documented opaque Bearer API key may be an
intentional custom authorization scheme. It must still have rotation, expiry or
revocation, audience/service binding, tenant binding, Scope checks, and TLS. Do
not describe this narrower scheme as full MCP OAuth conformance.

The official SDK provides `auth.RequireBearerToken`. Its `TokenVerifier` should:

- verify the token using the host service's authority;
- return `auth.ErrInvalidToken` for invalid credentials;
- populate stable user or key identity, scopes, expiration when available, and
  allowlisted context metadata;
- never pass an upstream token to another service.

Handlers read verified token information from `req.Extra.TokenInfo`; they must
not parse `Authorization` again.

## Logging and Errors

Allowlist metadata such as request ID, MCP method, Tool name, authenticated
tenant or subject identifier, result class, and duration. Never log:

- Authorization, API keys, cookies, refresh tokens, or token metadata;
- complete headers, request bodies, Tool arguments, or results;
- prompts, retrieved private content, model output, SQL parameters, or stacks;
- URLs containing query strings or fragments when they may carry data.

Keep client-visible errors stable and bounded. Authentication errors must not
reveal whether a tenant, key, or resource exists.

## External Content

Only Tools that fetch caller-selected network locations need SSRF, redirect,
DNS pinning, response decompression, and remote body-size defenses. Do not add
fetch-specific machinery to a server that only reads its own database. When a
Tool does fetch URLs, validate every redirect hop, block private and link-local
destinations, apply an egress policy, and treat returned content as untrusted.
