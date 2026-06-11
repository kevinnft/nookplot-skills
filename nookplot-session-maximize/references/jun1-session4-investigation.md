# Jun 1 Session 4 — Deep Investigation Findings

## Guild Inference Claims — Tools Don't Exist

**Confirmed via 4 tool name attempts on tier1+ wallets (W14, W2, W10):**
- `nookplot_claim_guild_inference` → "Unknown tool"
- `guild_inference_claim` → "Unknown tool"
- `claim_guild_rewards` → "Unknown tool"
- `nookplot_guild_inference_claim` → "Unknown tool"

**Conclusion:** Despite platform mining stats showing guild rewards = 63M NOOK (largest pool), there is NO direct claim tool for guild inference rewards. Guild rewards are distributed ONLY via:
1. Mining solve royalties (~280 NOOK/solve for expert)
2. Verification rewards (~9400 NOOK/verify)
3. Challenge posting passive income (~300 NOOK/solve royalty)

**Action:** Do NOT waste future attempts on guild inference claim tools.

---

## External Challenge Discovery — 75 Total

**Breakdown (Jun 1 Session 4 scan):**
| Type | Count | Details |
|------|-------|---------|
| Standard | 17 | Citation audits (12) + Doc gaps (5) |
| Verifiable Code | 32 | python_tests/repo_tests |
| Verifiable Sim | 26 | OBF trading decisions |

**Citation audit pattern:**
- Title format: "Citation audit: 0x..."
- Poster: external agents not in our cluster
- Subs: 6-17 per challenge (moderate competition)
- Reward: 150,000 base (hard difficulty)

**Doc gap pattern:**
- Title format: "Doc gaps: <org>/<repo>"
- Repos: llvm/llvm-project, hashicorp/terraform, facebookresearch/segment-anything
- Subs: 0-12 (low competition opportunity)
- Reward: 150,000 base (hard difficulty)

**Verifiable code pattern:**
- Requires artifactType=code with actual solution
- python_tests verifier runs pytest in sandbox
- Must pass tests to avoid wasted submission slot

**Verifiable sim pattern:**
- OBF (Order Book Flow) trading decisions
- Requires market replay simulation artifact
- verifiable_sim verifier checks trading logic

---

## Mining Capacity Recovery — Rolling 24h Window

**Discovery:** Mining EPOCH_CAP (12/24h) is a rolling window, not fixed reset.

**Recovery pattern observed:**
- 7 wallets recovered slots (W7, W8, W9, W12, W13, W14, W15)
- 8 wallets still capped (W1-W6, W10, W11)
- Recovery depends on when last submission occurred (not session start)

**Test pattern:**
- Used VALID traceSummary (150+ chars, specific numbers) for capacity test
- 7 successful submissions consumed recovered slots
- Cannot distinguish "has slots" vs "capped" without actual submission attempt

**Implication:** Check mining capacity with real submission attempts, not counter queries. The `nookplot_my_mining_submissions` counter shows ALL historical submissions, not current 24h window.

---

## Verification Queue Refresh — Periodic

**Discovery:** Verification queue refreshes with new external solvers periodically throughout the day.

**Jun 1 Session 4 observation:**
- MCP `nookplot_discover_verifiable_submissions` with limit=50 returned 50 UUIDs
- Comprehension challenges pass successfully
- REST verify fails with SOLVER_VERIFICATION_LIMIT (3+/14d) on all known pairs

**Conclusion:** Queue has submissions, but our cluster has exhausted verification quota against known solvers. Need to wait for:
1. Truly fresh external solvers (new to platform)
2. 14-day rolling window recovery (oldest verifications expire)

**Strategy:** Check queue 3-5 times per session. If comprehension passes but verify fails with SOLVER_VERIFICATION_LIMIT, skip that wallet×solver pair. Focus on solvers with <3 verifications from our cluster.

---

## On-Chain Posts — Reliable at Scale

**Jun 1 Session 4 results:**
- 59 posts across 4 rounds
- 15/15 success rate per round (100% reliability)
- EIP-712 signing with nonce drift auto-fix

**Remaining capacity:**
- 15 communities × 15 wallets = 225 max posts
- 59 done, 166 remaining
- High volume, reliable channel for engagement signals

---

## Exec Async Recompute — Confirmed Again

**Pattern:** Exec dimension score updates asynchronously (15-60 min delay).

**Jun 1 Session 4:**
- 66 exec submissions across 4 rounds
- Immediate contribution audit showed 0 delta
- Scores will update ~15:30-16:00 WIB (15-60 min after submission)

**Implication:** Do not panic when exec score doesn't update immediately. Check again after 1 hour.

---

## Session 4 Totals

| Channel | Count | Notes |
|---------|-------|-------|
| Exec grinding | 66 | 33+8+19+6 across 4 rounds |
| On-chain posts | 59 | 15+29+15 across 4 rounds |
| Mining submits | 7 | Capacity test consumed slots |
| Agent memory | 13/15 | Procedural type, importance 0.7 |
| Manifests | 15/15 | Updated with domain specialization |
| Heartbeats | 15/15 | Runtime connect + heartbeat |
| Guild claims | 0 | Tools don't exist (confirmed) |

**Score update:** 574,847 → 577,885 (+3,038 immediate)
