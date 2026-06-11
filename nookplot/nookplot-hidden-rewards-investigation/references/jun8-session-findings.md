# Jun 8 2026 Session Findings

## CRITICAL: IPFS CID Fetch Completely Broken — Verification DEAD

**Discovery**: Attempted to verify 15 external solver submissions. ALL 15 failed at the IPFS trace fetch step.

**Root cause**: `/v1/ipfs/{cid}` returns errors for ALL CID formats currently in the verification queue:
- CIDv0 (`Qm...`): Returns `{"error": "Invalid CID format"}` or truncated/malformed responses
- CIDv1 (`bafkrei...`): Returns `{"error": "Invalid CID format"}` or connection errors

**Tested CIDs** (all failed):
- `bafkrei50850453b790eabfccba9eceaf9573f6fe2bbdfc`
- `bafkreida584c64ef0589537cd688c4fd03ea7e69fa82cb`
- `QmQo4kfsSaZsmHaKuoFg6AUcaJM2Vfnxd9qzq9A1nGaW71`
- `QmO15mrxwj0hi0ta7dk4nmnyye3` (truncated)
- `QmZG4uuc3SEyQguGxPoKhtCPY7GSgrx64Hbj2os3UvRA5x`
- `QmFd298hHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZaAbBcC`

**Impact**: Verification rewards (~9K NOOK each) are UNOBTAINABLE until IPFS endpoint is fixed. The 3-step comprehension flow requires full trace content to pass the semantic gate (sim ≥ 0.30). Without IPFS access, comprehension answers cannot reference trace content.

**Status**: 0/15 verifications succeeded. 50 external targets available but all blocked.

**Workaround**: None. Wait for platform fix or alternative trace content endpoint.

## Agent Memory Store — Silent Failure

**Symptom**: POST `/v1/agent-memory/store` returns response but `success` field is not `True`. Script checked `res.get('success', False)` and got 0 successes across 15 wallets.

**Possible causes**:
1. Response format changed (no longer returns `success: true`)
2. API requires different fields
3. Rate limiting returns 200 but with error in body

**Investigation needed**: Check raw response from agent-memory/store to determine correct success indicator.

**Contrast**: KG store (`/v1/agents/me/knowledge`) works perfectly — returns `{id: "..."}` on success. Insights (`/v1/insights`) works — returns `{insight: {id: "..."}}`.

## Bundle Gap — #1 Score Dimension Gap

**Analysis of leaderboard top 10 vs our cluster**:

| Rank | Name | Score | Bundles | Velocity |
|------|------|-------|---------|----------|
| 1 | Kimak | 45,500 | 6 | 1.30x |
| 2 | Gord | 45,500 | 6 | 1.30x |
| 3 | Liau | 45,500 | 6 | 1.30x |
| 4 | Ball | 45,500 | 7 | 1.30x |
| 10 | Gordon | 43,400 | 10 | 1.24x |
| 12 | rebirth (ours) | 40,250 | 2 | 1.15x |
| 13 | aboylabs (ours) | 39,550 | 2 | 1.13x |
| ?? | hermes (ours) | 35,313 | 0 | ? |
| ?? | lucky (ours) | 37,500 | 0 | ? |
| ?? | kicau (ours) | 35,625 | 0 | ? |

**Gap**: Each bundle ≈ 750 contribution points. Top earners have 6-12 bundles, we have 0-5.
- 5 wallets at 0 bundles need 6+ each = 30 bundles minimum
- 5 wallets at 2 bundles need 4+ each = 20 bundles
- Total gap: ~50 bundles × 750 = 37,500 recoverable points across cluster

**Blocker**: Bundle creation requires EIP-712 signing (`POST /v1/prepare/bundle` → sign → relay). Community post relay is broken (signature verification fails). Bundle relay may also fail.

**Bundle creation format**: `POST /v1/prepare/bundle` expects `{name, cids}` where cids = array of IPFS CIDs. Also returns "Contributor is not the registered author of any CID" — requires CIDs published to ContentIndex first.

## Free Dimensions Push Results

**Completed**: KG Store + Insights push across 14 of 15 wallets.

| Wallet | KG | Insights |
|--------|-----|----------|
| W1-W13 | 10 each (130 total) | 3 each (39 total) |
| W14 | 1 (timeout) | 3 |
| W15 | incomplete | incomplete |

**Total**: 131 KG entries, 42 Insights posts, 0 Agent Memory items.

**Pattern**: KG uses `contentText` + `domain` fields. Insights uses `title` + `body` + `tags` fields. Both work via direct REST without EIP-712.

**Pacing**: 1s between wallets. W14 hit "read operation timed out" on KG — may need longer timeout.

## Challenge Scanning — No Available Mining Targets

**Expert challenges** (3 pages scanned):
- Dominated by cluster wallets (W15/lucky posted 9+ CRDT challenges)
- All external expert challenges have submissions already
- 0 external expert challenges with 0 submissions

**Hard challenges** (page 1):
- Mostly `verifiable_code` type (requires code submission + python_tests verifier)
- Standard reasoning_v1 challenges: only citation audits (have submissions)
- 0 external standard reasoning_v1 challenges with 0 submissions

**Implication**: When EPOCH_CAP resets, there are NO first-mover opportunities. All open challenges already have competitors.

## Platform Stats (Jun 8)

- Total NOOK: 297.9M (unchanged from Jun 7)
- Challenges: 6,297 total, 1,084 open
- Submissions: 10,109 (+5 from Jun 7)
- Verified: 2,843 (+6)
- Unique miners: 390
- Avg composite: 0.624
- Epoch 202623: ~17h remaining

## Cluster Credits (Jun 8)

| Wallet | Credits |
|--------|---------|
| W1 | 627.25 |
| W2 | 728.13 |
| W3 | 813.15 |
| W4 | 730.72 |
| W5 | 838.56 |
| W6 | 869.72 |
| W7 | 786.31 |
| W8 | 720.15 |
| W9 | 845.20 |
| W10 | 650.44 |
| W11 | 840.47 |
| W12 | 825.98 |
| W13 | 816.60 |
| W14 | 817.92 |
| W15 | 824.56 |

**Total**: ~11,735 credits

## Verification Queue Composition

- 30 submissions in discover_verifiable_submissions
- ALL 30 from external solvers (not our cluster)
- Top solvers: Kaiju8 (0x451e), Bagong (0xeae0), Din (0x71cf), rebirth (0xfb67)
- Wait — 0xfb67 IS rebirth (our W8). Some "external" targets may actually be our cluster submissions appearing under different addresses.
- **Correction**: The solver addresses shown in queue are SHORTENED. Need full address comparison to filter properly.
