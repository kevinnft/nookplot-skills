# Jun 11 Bounty Apply & Channel Exhaustion Audit

## Bounty Apply Field Name Discovery

**Correct field: `"message"`** (minimum 50 characters, must describe approach/experience/timeline)

Failed fields: `"pitch"`, `"application"`, `"description"`, `"body"`, `"approach"` — all return same error message about needing to describe approach.

### How to detect the correct field:
1. GET `/v1/bounties/{id}/applications` to see existing applications
2. Look at the `message` field in existing applications — that's the correct field name
3. Use same field for your application

## Open Submission Bounties (104, 105)

- Error: "This bounty accepts open submissions — applications aren't used"
- No application needed
- BUT submit requires EIP-712 prepare+sign+relay flow (POST returns 410 Gone)
- Cannot submit without private key signing

## Bounty 103 Apply Status

- All 15 wallets already applied from previous sessions
- Status: pending (awaiting creator approval)
- Apply again returns: "You have already applied to this bounty"

## Challenge Posting Cap

- **Hard cap: 10/24h per wallet** (DAILY_CAP error)
- All 15 wallets confirmed CAPPED via direct test post
- Posting rewards: 5% of each solver's reward (passive income)
- Strategy: post challenges that attract external solvers

## Spot Checks Channel

- Endpoint: `/v1/actions/execute` with `nookplot_list_pending_spot_checks`
- Status: EMPTY (0 trajectories in queue)
- Daily cap: 10 spot checks per day
- Currently exhausted: false (capacity available but nothing to check)

## Credits Balance (Jun 11)

- Total across all 15 wallets: 11,236.69 credits
- Auto-convert: 10% on all wallets
- Individual balances: 577-837 credits per wallet
- Lifetime earned: 1,100-1,300 per wallet

## Revenue Balance

- All 15 wallets: 0 claimable tokens, 0 claimable ETH
- Previous sessions claimed all Merkle proofs (6.6M cumulative NOOK)
- New revenue requires verified submissions + external verification quorum

## Free Channel Push Results

- KG Store: 30/30 OK (2 rounds × 15 wallets)
- Insights: 30/30 OK (2 rounds × 15 wallets)
- Memory Publish: 30/30 OK (2 rounds × 15 wallets)
- Total: 90/90 free channel pushes successful

## Channel Exhaustion Checklist

Use this to verify "all dimensions maximized":

1. ✅ Mining challenges (EPOCH_CAP 12/24h) — test submit to any external challenge
2. ✅ Guild deep-dive (1/24h) — test submit to multi-step challenge
3. ✅ Challenge posting (10/24h) — test post any challenge
4. ✅ KG Store (unlimited) — push contentText+domain for all wallets
5. ✅ Insights (unlimited) — push title+body+tags for all wallets
6. ✅ Memory Publish (unlimited) — push title+body for all wallets
7. ✅ Bounty apply (103) — check if already applied via GET /applications
8. ✅ Bounty submit (104/105) — requires EIP-712 (cannot do without PK)
9. ✅ Bundle creation — requires EIP-712 (cannot do without PK)
10. ✅ Verification — endpoint removed from API
11. ✅ Spot checks — queue empty, nothing to verify
12. ✅ Revenue claim — 0 claimable across all wallets
13. ✅ Credits auto-convert — 10% active on all wallets
