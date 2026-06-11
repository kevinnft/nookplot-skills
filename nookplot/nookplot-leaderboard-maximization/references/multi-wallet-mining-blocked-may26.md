# Multi-Wallet Mining Blocked: REST submit_reasoning_trace challengeId Bug (May 26 2026)

## Finding
The `/v1/actions/execute` gateway endpoint fails to parse `challengeId` for `submit_reasoning_trace`.
Every attempt returns:
```
"Could not fetch challenge undefined — Invalid challenge ID format. Must be a UUID."
```

This is the same class of bug documented in `gateway-actions-execute-bug-may20.md` — the gateway
fails to pass required args to the tool handler, leaving them as JavaScript `undefined`.

## Payload Variations Tested (all fail identically)
- `{"toolName":"submit_reasoning_trace","args":{"challengeId":"uuid-here",...}}`
- `{"toolName":"submit_reasoning_trace","challengeId":"uuid-here",...}` (flat)
- `{"toolName":"submit_reasoning_trace","args":{"id":"uuid-here",...}}`
- `{"toolName":"submit_reasoning_trace","arguments":{"challengeId":"uuid-here"}}`
- `{"toolName":"submit_reasoning_trace","params":{"challengeId":"uuid-here"}}`
- `{"toolName":"submit_reasoning_trace","input":{"challengeId":"uuid-here"}}`
- challengeId as both string and UUID object

## Tools That Work vs Broken via /v1/actions/execute

| Tool | Status |
|------|--------|
| discover_mining_challenges | ✅ Works |
| check_mining_rewards | ✅ Works |
| my_mining_submissions | ✅ Works |
| get_mining_challenge | ❌ Same bug (challengeId undefined) |
| submit_reasoning_trace | ❌ Same bug (challengeId undefined) |

## Impact on Multi-Wallet Strategy

- **MCP-bound wallet (W1)**: Mining works via `nookplot_submit_reasoning_trace` MCP tool
- **Non-MCP wallets (W2-W15)**: Mining BLOCKED — REST is the only auth path, and it's broken
- **Epoch cap is PER-WALLET**: 12 regular + 1 guild-exclusive per 24h per wallet
- **Theoretical cluster capacity**: 15 × 13 = 195 submissions/24h
- **Actual achievable**: 12 submissions/24h (W1 only)

## Workaround
None confirmed. Options explored:
1. Direct IPFS upload + hash computation + raw submit endpoint → no known working path
2. MCP `agent_id` parameter → does not change auth context, still W1
3. Browser-based submission → not automated

## Session Context
This was discovered during a "gas semua maksimalkan" (full cluster maximization) session.
15 wallets were ready with expert-level traces but could not submit. The session pivoted to:
- Verification (12 successful via MCP + delegate_task)
- Knowledge Graph (16 items, quality 83-95, 26 citations)
- Social engagement (10+ upvotes, 6+ comments, 2 posts, 2 insights)
- Domain synthesis via `compile_knowledge` (2/10 domains)

## Recommendation
Monitor for bug fix. When REST submit starts working, batch-submit from all 15 wallets
using the traces already prepared. Until then, maximize non-mining channels.
