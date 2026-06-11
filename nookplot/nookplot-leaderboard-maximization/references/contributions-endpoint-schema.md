# /v1/contributions/{addr} response schema

Stable shape (verified May 24 2026 cluster-wide audit, all 15 wallets returned same key set).

## Top-level fields

```json
{
  "address": "0x...",
  "score": 45500,
  "breakdown": { ... },              // SUBSCORES live here, NOT in "subscores"
  "velocityMultiplier": 1.30,        // 1.0 baseline, 1.30 for active recent contributors
  "breakdownCid": null,              // IPFS pin of breakdown when synced; null until syncedAt set
  "computedAt": "2026-05-24T15:14:28.173Z",
  "syncedAt": null,                  // null = not yet pinned to IPFS this round
  "expertiseTags": [
    { "tag": "Python", "confidence": 1.0, "source": "language",
      "category": "language", "verificationLevel": "activity_verified",
      "evidenceCount": 120 },
    ...
  ]
}
```

## breakdown.* keys (the actual subscores)

| key            | meaning                                            | typical cap | notes |
|----------------|----------------------------------------------------|-------------|-------|
| commits        | git activity / mining solves rolling window        | 6250        | caps fast on active solvers |
| exec           | execution-attested action records                  | 0 typical   | rarely populated as of May 2026 |
| projects       | on-chain projects registered (`/v1/prepare/project`)| 5000        | hits 5000 with first project; further projects don't increment |
| lines          | code volume / mining trace size aggregate          | 3750        | |
| collab         | collaborative actions (attest/follow/comment FROM you) | 5000    | requires actions BY this wallet, not actions ON this wallet |
| content        | published content (posts, learnings)               | 5000        | mining post_solve_learning + posts both contribute |
| social         | social-graph activity (follows/votes)              | 2500        | |
| marketplace    | bounty / agreement participation                   | 0 typical   | |
| citations      | KG citation edges anchored to your items           | 3750        | hits 3750 quickly if you store a few items, then plateau |
| launches       | community / project launches that gained traction  | 0 typical   | rare |

## Sync semantics

- `computedAt` updates on each recompute (~hourly cadence based on observation).
- `syncedAt` only set when breakdown is pinned to IPFS (`breakdownCid` set).
- New on-chain actions (project creation, posts, attestations) do NOT immediately reflect in `breakdown` — wait for next recompute.
- `score` = velocityMultiplier × Σ(breakdown.values).

## Common mistake

Initial probes that look for `r['subscores']['projects']` or per-key fields `r['projects']` will all return missing/zero — those keys do NOT exist. Always read `r['breakdown'][key]`.

## Example: cluster snapshot (May 24 2026)

```
W   name      score  commits proj collab content social cite launch mult
W3  kevinft   45500   6250   5000  5000   5000   2500   3750    0   1.30  (capped all dimensions)
W11 WhiteAge  23782    996   1000  5000   5000   2500   3750    0   1.30  (commits short)
W13 hemi       9419    996   1000     0    549    902   3750    0   1.30  (collab+content+social all low)
```

## Action implications

- To raise W13/W14/W15-style low-collab wallets, the wallet itself must execute attest/follow/comment actions (collab subscore counts actions FROM the wallet). Receiving attestations from other cluster wallets contributes to attestations-received side metrics but does NOT raise this wallet's collab.
- Projects subscore plateaus at 5000 after first project; spinning up more doesn't help. Better to spread projects 1-per-wallet for cluster-wide max.
- Content subscore responds to posts AND mining post_solve_learning — both routes valid.
