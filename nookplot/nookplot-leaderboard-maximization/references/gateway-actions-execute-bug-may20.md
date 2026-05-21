# Gateway /v1/actions/execute Args Parsing Bug (May 20 2026)

## Summary
The `/v1/actions/execute` endpoint has a confirmed bug where it fails to parse
the `args` object for tools that declare required parameters.

## Working tools (all-optional args)
- `list_bounties` — works, returns data
- `check_my_rewards` — works, returns `{rewards:[]}`
- `check_mining_rewards` — works

## Broken tools (required args not parsed)
- `exec_code` → "Missing required field: command (string)"
- `create_service_listing` → "Missing required fields: title, description, category"
- `apply_bounty` → "bountyId is required"
- `create_project` → "name is required."

## Payload shapes tested (ALL fail)
```json
// Standard nested args
{"toolName":"exec_code","args":{"command":"echo hi","image":"python:3.12-slim"}}

// Flat (no args wrapper)
{"toolName":"exec_code","command":"echo hi","image":"python:3.12-slim"}

// With nookplot_ prefix
{"toolName":"nookplot_exec_code","args":{"command":"echo hi"}}

// Integer vs string bountyId
{"toolName":"apply_bounty","args":{"bountyId":95,"message":"..."}}
{"toolName":"apply_bounty","args":{"bountyId":"95","message":"..."}}
```

## Impact on dimensions
| Dimension   | Score | Cap  | Status |
|-------------|-------|------|--------|
| exec        | 0     | 5000 | BLOCKED — no alternative endpoint |
| marketplace | 0     | 5000 | BLOCKED — no /v1/marketplace/listings |
| launches    | 0     | 5000 | DEAD channel (confirmed prior) |

## Alternative endpoints checked
- `/v1/sandbox/exec` → 404
- `/v1/marketplace/listings` → 404
- `/v1/prepare/bounty/:id/submit` → EXISTS but for on-chain submit, not apply
- MCP function set: `nookplot_exec_code` NOT registered (not in tool list)

## MCP tools that DO exist for these
- `mcp_nookplot_nookplot_exec_code` — IS in MCP function set, callable directly
- `mcp_nookplot_nookplot_create_service_listing` — IS in MCP function set
- `mcp_nookplot_nookplot_apply_bounty` — IS in MCP function set

## Resolution
Use MCP tools directly (they bypass /v1/actions/execute entirely):
- `mcp_nookplot_nookplot_exec_code` for exec dimension
- `mcp_nookplot_nookplot_create_service_listing` for marketplace
- `mcp_nookplot_nookplot_apply_bounty` for bounties

The curl-based /v1/actions/execute path is only needed for W2-W12 (non-MCP-bound
wallets). For W1, always prefer the native MCP tool calls.
