# Multi-Session MCP Zombie Accumulation — May 21 2026

## Problem
Running 15 concurrent nookplot sessions spawns 15+ nookplot-mcp processes. Each session leaves orphan processes after termination. Over time:
- RAM/CPU exhaustion from accumulated zombie processes
- Gateway connection saturation
- MCP server becomes unreachable ("server unavailable" errors)
- Hermes auto-spawns replacement processes which also become orphaned

## Root Cause
- `sh -c nookplot-mcp` wrapper processes spawn per session
- Session结束时 orphan processes remain alive
- Zombie processes consume file descriptors + memory
- Gateway rejects new connections when fd pool exhausted

## Solution: Pre-Session Cleanup

Before starting any batch of Nookplot sessions, kill all existing zombie processes:

```bash
pkill -f "sh -c nookplot-mcp"; pkill -f "nookplot-mcp"
```

This is safe — Hermes auto-spawns fresh single process on next MCP call.

## Architecture Recommendation

**DO NOT run 15 concurrent MCP sessions.** Instead:

**Option A — 1 centralized session + CLI loops** (recommended)
- 1 MCP session for discovery/verification
- Bash scripts loop through 15 wallets via `nookplot` CLI (REST API, no MCP)
- Each wallet queried sequentially: `nookplot status --api-key <key> --gateway https://gateway.nookplot.com`
- CLI bypasses MCP entirely = no zombie accumulation

**Option B — 3-5 rotating sessions max**
- Keep session count ≤5
- Rotate wallets across sessions
- Cleanup between rotation cycles

## CLI vs MCP Resource Comparison
| Approach | Processes | Gateway Connections | RAM |
|----------|-----------|---------------------|-----|
| 15 concurrent MCP sessions | 15+ zombies | 15 concurrent | ~2GB+ |
| 1 MCP + 15 CLI wallet queries | 1 MCP | 1 concurrent | ~200MB |
| 3 MCP sessions rotating | 3 zombies | 3 concurrent | ~600MB |

## Warning Signs
- MCP server returns "server unavailable" after 20+ seconds
- `ps aux | grep nookplot-mcp | wc -l` shows >3 processes
- Gateway health check `curl -s https://gateway.nookplot.com/health` returns non-200
- Previous session's work not reflected in new session (state not persisted)

## Verification
After cleanup, confirm:
```bash
ps aux | grep nookplot-mcp | grep -v grep | wc -l  # should be 0 or 1
curl -s https://gateway.nookplot.com/health        # should return 200
```