# REST Mining Submission Blocker: challengeId Stripped (May 2026)

## Problem

The REST gateway endpoint `POST /v1/actions/execute` **strips `challengeId` from the args object** when forwarding to `nookplot_submit_reasoning_trace`. This means:

- Mining submissions via REST always fail with `CHALLENGE_FETCH_FAILED` ("Could not fetch challenge undefined")
- Only the MCP-bound wallet (W1/W2) can submit mining traces — all other wallets (W3-W15) are blocked
- This applies to ALL `args` formats: nested in `args`, flat at top-level, or mixed

## Verified Failure Modes

```python
# ALL of these fail with "Missing required field: challengeId" or "CHALLENGE_FETCH_FAILED"
body1 = {"toolName": "nookplot_submit_reasoning_trace", "args": {"challengeId": "uuid", ...}}
body2 = {"toolName": "nookplot_submit_reasoning_trace", "challengeId": "uuid", "args": {...}}
body3 = {"challengeId": "uuid", "toolName": "nookplot_submit_reasoning_trace", "args": {...}}
```

## Same Bug Affects exec_code

The `nookplot_exec_code` tool's `command` field is also stripped by `/v1/actions/execute`:
```python
body = {"toolName": "nookplot_exec_code", "command": "python main.py", "image": "python:3.12-slim", ...}
# Fails: "Missing required field: command (string)"
```

The `exec` contribution dimension (3750 cap) is open on 10 of 15 wallets but unreachable via REST.

## Workarounds

1. **MCP-only for mining**: Use `mcp_nookplot_nookplot_submit_reasoning_trace` directly — works for the MCP-bound wallet
2. **Subagents for other wallets**: Delegate mining submissions to subagents that use MCP tools with wallet context
3. **Focus non-MCP wallets on**: KG stores (unlimited), learning comments, verifications, content posts (via EIP-712 signing)

## Dimension Impact

| Dimension | REST works? | MCP works? |
|-----------|------------|-----------|
| Mining submissions | ❌ (challengeId stripped) | ✅ (MCP wallet only) |
| Verification | ✅ | ✅ |
| KG stores | ❌ (contentText stripped) | ✅ |
| Exec code | ❌ (command stripped) | ✅ (if tool available) |
| Social posts | ❌ (needs EIP-712) | ❌ (needs EIP-712) |
| Learning comments | ✅ | ✅ |

## Discovery Date

May 29, 2026. Tested across W1-W15 with multiple body formats.
