# MCP Conformance CLI Compatibility

<!-- cli-compatibility-contract:v1 -->

| Field | Value |
| --- | --- |
| Command | `npm exec --package=@modelcontextprotocol/conformance -- conformance` |
| Distribution | `@modelcontextprotocol/conformance` |
| 本机验证版本 | `0.2.0-alpha.11` |
| 验证日期 | 2026-09-04 |
| Current source baseline | `0.2.0-alpha.11` as of 2026-09-04 |
| Purpose | Supplementary MCP server/client conformance checks |

The alpha version is recorded because the stable `0.1.x` line does not cover
the complete `2026-07-28` requirement set. It is not a claim of general alpha
stability.

## 关键能力

Before using the runner, inspect without changing a project dependency file:

```text
npm exec --yes --package=@modelcontextprotocol/conformance@0.2.0-alpha.11 -- conformance --version
npm exec --yes --package=@modelcontextprotocol/conformance@0.2.0-alpha.11 -- conformance list --requirements 2026-07-28
npm exec --yes --package=@modelcontextprotocol/conformance@0.2.0-alpha.11 -- conformance server --help
```

`npm exec` may download packages and contact a registry. Obtain the task's required
authorization and use the environment's approved registry. Do not commit npm
caches, `node_modules`, result directories, or credentials.

For a product server, run only scenarios applicable to advertised capabilities
and the selected authorization mode. A full SDK requirement set may expect
fixture Tools or OAuth behavior that an internal API-key product intentionally
does not expose.

## 版本不一致时

- If another version provides `list --requirements`, `--spec-version`, and
  server-mode wire-schema validation, it may be used after recording that the
  version is outside this baseline.
- If those capabilities are missing, do not claim `2026-07-28` conformance from
  the run. Fall back to official SDK client integration tests and raw protocol
  tests.
- Do not auto-upgrade the runner, Node.js, npm, or the project's SDK. Inspect
  release notes and update this contract when establishing a new baseline.
