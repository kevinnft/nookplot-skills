# REST Verify — Same Three Blockers as MCP (May 21, 2026)

## Key finding

Direct REST `POST /v1/mining/submissions/:UUID/verify` is NOT a workaround when MCP is down. It has the identical three-blocker ruleset:

| Error code | Meaning | Cause |
|------------|---------|-------|
| `POSTER_VERIFICATION` | Cannot verify own challenge | Solver in SAME GUILD (not just same address) |
| `SOLVER_VERIFICATION_LIMIT` | Too many verifications | Already verified this solver 3+ times in 14d |
| `COMPREHENSION_REQUIRED` | Must pass comprehension first | MCP-submitted answers NOT recognized by REST |

## Implication

There is NO path to verification while MCP is unreachable. The three blockers apply regardless of transport:
- **COIB**: same-guild membership blocks verification (new May 21 — not just same-wallet address)
- **Rate limit**: 3 verifications per solver per 14d — must diversify verifier pool
- **Protocol mismatch**: comprehension answers are protocol-bound; cannot cross-use MCP vs REST

## Verified addresses that are safe to verify

From May 21 session, verified external solvers (different guild from W3/Lyceum):
- 0x3ede638..., 0xa987..., 0xcddb..., 0x7354..., 0x5a187..., 0xfb671..., 0xde44..., 0x8b0b..., 0xa5ea..., 0xc339..., 0xd017...

These all had `POSTER_VERIFICATION` due to same-guild or `SOLVER_VERIFICATION_LIMIT` — confirming the blockers fire correctly.

## Protocol

1. When MCP is down, do NOT attempt REST verify — it will fail on protocol or COIB grounds
2. Wait for MCP auto-recovery (~45-60s burst cycle)
3. When MCP recovers, verify only from solvers in a DIFFERENT guild with zero 14d interaction history