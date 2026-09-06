# Forward Evaluation Prompts

Compare the revised Skill with the previous version and with no Skill. Record
whether official current sources were checked, the selected protocol and SDK
were pinned, repository constraints were preserved, and security-sensitive data
was kept out of logs.

## Should Trigger

1. "Add a `memory_search` MCP Tool to this existing Gin service. Use the newest
   stable MCP protocol, keep its API-key tenant boundary, and support the prior
   protocol revision."
2. "Build a local Go MCP subprocess that exposes two read-only filesystem
   resources over stdio; do not add an HTTP listener."
3. "Review this Go Streamable HTTP MCP server: it logs every Tool argument,
   accepts any Origin, and still uses session IDs with MCP 2026-07-28."

## Should Not Trigger

1. "Add an ordinary JSON REST health endpoint to this Go service."
2. "Explain what MCP means in manufacturing process control."
3. "Create a TypeScript MCP server; no Go code is involved."

## Expected Improvements

- Chooses the official Go SDK by default instead of a hard-coded third-party SDK.
- Verifies current official sources instead of treating this package's baseline
  as permanently latest.
- Distinguishes Streamable HTTP 2026 lifecycle from legacy sessions.
- Does not log complete requests or results.
- Uses repository architecture rather than forcing a standalone directory tree.
