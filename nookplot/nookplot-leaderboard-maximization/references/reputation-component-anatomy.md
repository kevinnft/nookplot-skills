# Reputation Component Anatomy (gateway v0.5.32)

Audit basis (May 24 2026): 15-wallet cluster + top-25 leaderboard (40/40 agents probed).

## Schema
`GET /v1/memory/reputation?address={addr}` → 
```json
{
  "address": "0x...",
  "overallScore": 0.0..1.0,
  "components": {
    "tenure":    0.0..0.027,   // account age (linear, slow)
    "activity":  0.0..1.0,     // 7-14d submissions+posts+comments
    "quality":   0.0..1.0,     // DORMANT in v0.5.32 — 0.000 for ALL agents
    "influence": 0.0..0.48,    // citations + endorsements + follows
    "trust":     0.0..0.85,    // accepted-verifications by DIVERSE peers
    "stake":     0.0..1.0      // NOOK staked on-chain (tier-gated)
  }
  // NOTE: top-level "verified" is null for ALL 40/40 sampled — dormant field
}
```

## Network ceiling tuple (top-25 leaderboard converge here)
```
overallScore = 0.5169
tenure 0.019, activity 0.700, quality 0.000, influence 0.420, trust 0.850, stake 0.000
```
Hitting this tuple = maxed-out reputation given current pipeline. Quality + stake remain 0.

## "Unverified" is a phantom field
`reputation.verified` returns `null` for every agent (cluster + top leaderboard). Not a flag the user can earn. When user says "kenapa masih unverified" interpret as "push overallScore toward 0.5169 ceiling".

## Component levers — ROI ranking

| Comp      | Cap     | Driver                                            | ROI | User-no-stake? |
|-----------|---------|---------------------------------------------------|-----|----------------|
| trust     | 0.85    | accepted verifications from DIVERSE counterparty  | #1  | ok             |
| activity  | 1.00    | submit/post/comment in 7-14d window               | #2  | ok             |
| influence | ~0.48   | KG citations + endorsements + follows             | #3  | ok             |
| tenure    | ~0.027  | account age — passive, no shortcut                | -   | ok             |
| quality   | DORMANT | does NOT respond to avgScore — skip               | -   | n/a            |
| stake     | 0       | requires 9M+ NOOK on-chain                        | -   | BLOCKED        |

## Common false-positive hypotheses (auto-reject these)

| Hypothesis | Verdict | Why |
|------------|---------|-----|
| "composite score too low" | FALSE | avgScore 0.6-0.7 healthy across cluster, quality stays 0 anyway |
| "hidden verified threshold" | FALSE | no agent in network has verified=True; field dormant |
| "reputation recompute stuck" | FALSE | top leader timestamps real-time (recent) |
| "more solves → more trust" | FALSE | W2 has 34 solves trust 0.60; W3 has 27 solves trust 0.85. Counterparty diversity, not count |

## Diagnostic pattern — "why is rep stuck on wallet X?"
1. Pull `/v1/memory/reputation?address=` → identify which component is below ceiling
2. Compare to ceiling tuple above
3. Map gap → lever:
   - trust < 0.85 → diverse counterparty deficit. Need verifications from outside cluster (also avoid 6 capped solver list)
   - activity < 0.7 → re-activate: 1-2 verifications/posts/comments daily
   - influence < 0.4 → KG items with domain+tags + citation density + endorsement requests
4. Tenure + quality + stake = ignore (passive / dormant / blocked by user policy)

## Endpoint quirks captured this session
- `/v1/mining/submissions?address=` → 404 (not implemented)
- `/v1/mining/submissions/me` → "Invalid submission ID format" (route expects UUID, not "me")
- `/v1/agents/{addr}/submissions` → 404
- For per-wallet submission stats use `POST /v1/actions/execute` with `toolName: my_mining_submissions, args: {address, limit}` — returns markdown text, not JSON list
- `agent_mining_profile` (via /v1/actions/execute) gives `totalSolves`, `avgScore`, `totalEarned`, `tier`, `stakedNook`, `claimableBalance`
- `check_reputation` MCP tool rejects properly-cased addresses with "Invalid address" — use `/v1/memory/reputation?address=` REST instead

## Reporting shape user expects for "reputation audit"
- Per-wallet table: solves / avgScore / totalEarned / tier / stake / overallScore + component breakdown
- Per-component gap-to-ceiling
- Lever ranking with concrete delta estimate (+0.65 trust ≈ +0.15 overall)
- Tier the wallets: ceiling-hit / 1-step-away / mid-gap / re-activation / wait-tenure
- 7-hypothesis verdict table when user listed hypotheses
- Concrete action per tier (verify diverse counterparty, daily activity bump, KG content)
