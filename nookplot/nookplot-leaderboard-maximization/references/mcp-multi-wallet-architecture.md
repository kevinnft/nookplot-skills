# MCP Multi-Wallet Architecture (May 2026)

## Problem: Shared MCP Bottleneck

When 15 subagent sessions share 1 nookplot-mcp server:
- stdio transport is single-threaded — all requests serialize through one process
- 15 parallel subagents hammer the shared MCP → timeout → restart loop
- Each restart triggers Hermes to spawn a new session → more parallel load → cascade
- MCP "unreachable" errors are a SYMPTOM, not the cause

## Root Cause Identified (May 21 2026)

Multiple subagents simultaneously verify submissions from the same solver address (W10 joni, 0x5fcF...).
All hit the per-solver 3/14d verify cap → all get error → all retry simultaneously → retry storm
→ MCP stdio queue backs up → Hermes marks MCP unreachable → restarts → crash loop.

See: `solver-verification-limit-14d.md`

## Solution: Per-Wallet MCP Isolation

Each subagent session gets its own MCP server authenticated as a different wallet.

### Credential Storage

```
~/.nookplot/credentials.json              → W1 (global/default)
~/.nookplot/agents/w2/credentials.json    → W2
~/.nookplot/agents/w3/credentials.json    → W3
...
~/.nookplot/agents/w15/credentials.json   → W15
```

Each credentials.json:
```json
{
  "address": "0x...",
  "privateKey": "0x...",
  "apiKey": "nk_...",
  "gatewayUrl": "https://gateway.nookplot.com"
}
```

### Switching Wallets via Environment

```bash
# Per subagent session
NOOKPLOT_PROFILE=w2 npx -y @nookplot/mcp@latest
# → Connected as wallet W2 address

# In Hermes subagent spawn:
{
  "goal": "Mining task for wallet W2",
  "context": "Set NOOKPLOT_PROFILE=w2 before any nookplot tool call"
}
```

`NOOKPLOT_PROFILE` maps to `~/.nookplot/agents/<profile>/credentials.json`.

### Verification: Which Wallet Am I?

```bash
NOOKPLOT_PROFILE=w3 nookplot-mcp 2>&1 | grep "Connected as"
# → [nookplot-mcp] Connected as 0x...
```

## Setup After Adding New Wallet

```bash
# Create all per-wallet credentials from nookplot_wallets.json
mkdir -p ~/.nookplot/agents
# See scripts/setup-per-wallet-credentials.sh
```

## Architecture Summary

```
Subagent 1 → NOOKPLOT_PROFILE=w1 → MCP server (wallet W1) → gateway
Subagent 2 → NOOKPLOT_PROFILE=w2 → MCP server (wallet W2) → gateway
...
Subagent 15 → NOOKPLOT_PROFILE=w15 → MCP server (wallet W15) → gateway
```

Each MCP → its own gateway connection. Parallel, not serialized. No shared stdio bottleneck.

## Known Constraints

- MCP via npx has ~2-5s startup latency per spawn
- Pre-warm MCP before launching parallel subagents to avoid timeout cascade
- Gateway connectivity: `https://gateway.nookplot.com` (reachable), `https://api.nookplot.com` (NXDOMAIN)
