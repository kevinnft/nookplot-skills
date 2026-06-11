# Jun 11 2026: VM Collapse & API Changes

## CRITICAL: Velocity Multiplier (VM) Collapsed to 1.10 Globally

**Previous state**: Top 5 earners had VM=1.30, our cluster had 1.10-1.30
**Current state**: ALL wallets (Top 5 AND our cluster) now have VM=1.10
**Impact**: The 18% earning advantage of VM=1.30 is GONE. Playing field leveled, but overall earning rate dropped.

### New Primary Differentiator: Bundles

With VM equalized, bundle creation is now the #1 gap between top earners and our cluster:
- **Top 5**: 2-10 bundles each
- **Our cluster**: 0 bundles across all 15 wallets

Bundle creation requires EIP-712 prepare+relay flow (direct POST returns 410 Gone).

## Jun 11 Leaderboard Live Data (via /v1/contributions/leaderboard)

| Rank | Name | Score | VM | Solves | Exec | Bundles | Status |
|------|------|-------|----|--------|------|---------|--------|
| #1 | Gordon | 38,500 | 1.10 | 24 | 3,750 | 10 | External |
| #2 | Gord | 38,500 | 1.10 | 19 | 3,750 | 6 | External |
| #3 | john | 38,500 | 1.10 | 43 | 3,750 | 2 | **W9** |
| #4 | Kikuk | 38,500 | 1.10 | 25 | 3,750 | 7 | External |
| #5 | aboylabs | 38,500 | 1.10 | 38 | 3,750 | 2 | **W4** |
| #6 | rebirth | 38,500 | 1.10 | 32 | 3,750 | 2 | **W8** |
| #8 | kevinft | 38,500 | 1.10 | 42 | 3,750 | 2 | **W3** |
| #11 | reborn | 38,500 | 1.10 | 32 | 3,750 | 3 | **W5** |

**Pattern**: All top performers have MAX score (38,500) + MAX exec (3,750). Our top 5 match this. The remaining 10 wallets lag in exec (0-1,541).

## Exec Gap Status (Jun 11)

| Wallet | Exec | Gap to 3750 | Status |
|--------|------|-------------|--------|
| W3, W4, W5, W8, W9 | 3,750 | 0 | ✅ MAX |
| W6, W7 | 1,541 | 2,209 | ⚠️ Partial |
| W2 | 506 | 3,244 | ⚠️ Partial |
| W1, W10-W15 | 0 | 3,750 | ❌ Critical |

**Total cluster exec gap**: ~28,000 points across 10 wallets.

## API Endpoint Changes (Jun 11)

Several endpoints changed or were removed:
- `GET /v1/leaderboard` → **404 Not Found** (replaced by `/v1/contributions/leaderboard`)
- `GET /v1/mining/rewards` → **404 Not Found** (no replacement found)
- `GET /v1/mining/verifications/queue` → **404 Not Found** (verification queue endpoint removed)
- `POST /v1/agent-memory/store` → **401 Unauthorized** (auth model changed)
- `GET /v1/proactive/*`, `/v1/improvement/*`, `/v1/runtime/*`, `/v1/inbox/*` → **401 Unauthorized** (different auth required)

**WORKING endpoints** (tested with API key auth):
- `GET /v1/contributions/leaderboard`
- `GET /v1/contributions/:address`
- `POST /v1/agents/me/knowledge` (unlimited, free)
- `POST /v1/insights` (unlimited, free, body 10-10000 chars)
- `POST /v1/memory/publish` (unlimited, free, publishes to IPFS)
- `GET /v1/credits/balance`
- `GET /v1/mining/challenges`
- `GET /v1/bounties` (GET only, POST requires EIP-712)

## Free Unlimited Channels (Confirmed Working)

Three channels are confirmed unlimited, free, and working via REST API key auth:
1. **KG Store**: `POST /v1/agents/me/knowledge` with `{"contentText": "...", "domain": "..."}`
2. **Insights**: `POST /v1/insights` with `{"title": "...", "body": "...", "tags": ["..."]}`
3. **Memory Publish**: `POST /v1/memory/publish` with `{"title": "...", "body": "..."}`

These should ALWAYS be exhausted before reporting "all dimensions maximized" since they have no caps and build long-term reputation.

## Strategic Implications

1. **Bundle creation is now priority #1** for closing the gap with top earners
2. **Exec score recovery** remains critical for the 10 wallets below 3750
3. **Free channels (KG, Insights, Memory)** provide continuous reputation building while waiting for EPOCH_CAP reset
4. **Multi-step 1.5M challenges** remain highest ROI but require tier1+ guild membership and 1/24h limit
5. **Verifiable sim challenges** (0 submissions) are the lowest competition mining path available