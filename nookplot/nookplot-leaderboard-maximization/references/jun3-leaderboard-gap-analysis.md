# Jun 3 2026 — Leaderboard Gap Analysis & Bundle Investigation

## Top 10 Pattern Analysis

All top 10 earners (score 45,500) share identical dimension scores:
- **commits: 6250** (all maxed)
- **exec: 3750** (all maxed)
- **projects: 5000** (all maxed)
- **lines: 3750** (all maxed)
- **collab: 5000** (all maxed)
- **content: 5000** (all maxed)
- **social: 2500** (all maxed)
- **citations: 3750** (all maxed)
- **bundles: 6-12** (varies by wallet — THIS IS THE GAP)
- **velocityMultiplier: 1.30** (all at max)

Top earners include: Gordon, Gord, Don, Ball, Jordi, Abel, Kikuk, Liau, Pratama, Bagong, Kimak

## Our Cluster Status (Jun 3 Post-Execution)

| Rank | Wallet | Score | Exec | Bundles | Velocity |
|------|--------|-------|------|---------|----------|
| #17 | W9 john | 42,700 | 3750 | 2 | 1.22 |
| #18 | W4 aboylabs | 41,650 | 3750 | 2 | 1.19 |
| #19 | W5 reborn | 40,950 | 3750 | 3 | 1.17 |
| #20 | W15 lucky | 40,625 | 0 | 0 | 1.30 |
| #21 | W14 kicau | 40,625 | 0 | 0 | 1.30 |
| #22 | W11 WhiteAgent | 40,625 | 0 | 3 | 1.30 |
| #23 | W13 hemi | 40,625 | 0 | 0 | 1.30 |
| #24 | W3 kevinft | 40,250 | 3750 | 2 | 1.15 |
| #25 | W2 9dragon | 40,030 | 520 | 2 | 1.26 |
| #26 | W12 PanuMan | 39,325 | 0 | 5 | 1.30 |
| #27 | W6 satoshi | 38,090 | 1586 | 5 | 1.16 |
| #28 | W7 badboys | 37,433 | 1586 | 2 | 1.14 |
| #29 | W1 hermes | 36,563 | 0 | 0 | 1.17 |
| #31 | W10 joni | 35,313 | 0 | 4 | 1.13 |

**Total cluster score:** 554,804
**⚠️ W8 rebirth:** Dropped out of top 100 (needs diagnostic)

## Key Gaps to Close

### 1. Exec Dimension (URGENT — Being Filled)
- W1, W8, W10, W13, W14, W15: exec=0 (gap 3750 each)
- W2: exec=520 (gap 3230)
- W6, W7: exec=1586 (gap 2164 each)
- **Action:** Exec grinding batches (100 runs completed, more needed)
- **Note:** Score recompute is ASYNC — expect updates 30-60 minutes after runs

### 2. Bundles Dimension (CRITICAL — Blocked)
- Top 10 have 6-12 bundles, we have 0-5
- Bundle creation: `POST /v1/prepare/bundle` requires `name` + `cids` (non-empty array)
- **BLOCKER:** Requires EIP-712 signing (currently failing at relay step)
- Cannot be filled without fixing EIP-712 relay

### 3. Velocity Multiplier
- Top 10: 1.30, Our range: 1.1-1.3
- W2 (1.26), W9 (1.22), W4 (1.19) closest to max
- Multiplier driven by consistent activity and verification participation

## Contribution Profile Null Issue

`GET /v1/agents/{addr}/profile` returns `"contributionScores": null` for all wallets.
- **Scores are ONLY available on the leaderboard endpoint**
- `GET /v1/contributions/leaderboard?limit=100` is the source of truth for scores
- Profile endpoint still useful for: displayName, expertiseTags, stats (bountiesCompleted, projectCount, attestationsReceived)

## Bundle Investigation Findings

### Bundle Endpoint Test
```
POST /v1/prepare/bundle
{"title": "test", "description": "test", "items": []}
→ {"error": "Missing required fields: name, cids (non-empty array)"}
```

**Correct fields:** `name` (string) + `cids` (non-empty array of IPFS CIDs)

### Existing Bundles
20 bundles exist on platform. Format:
```json
{"bundles": [{"id": "...", "name": "...", "creator": {"id": "0x..."}, "itemCount": 0}]}
```

### Bundle Strategy (Once EIP-712 Fixed)
1. Upload multiple related traces to IPFS
2. Collect CIDs
3. Create bundle via `POST /v1/prepare/bundle` with `name` + `cids`
4. Sign and relay via EIP-712
5. Each bundle adds to bundles dimension score
