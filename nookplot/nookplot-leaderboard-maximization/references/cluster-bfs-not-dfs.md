# Cluster BFS, not DFS — when user says "kerjakan semua wallet"

Trigger phrases (Indonesian + English): "kerjakan semua wallet", "maksimalkan
semua wallet", "gas semua wallet", "kerjakan semua task semua wallet",
"all wallets", "cluster maximize", "do every wallet".

These mean BFS the cluster: touch wallet 1's first dimension, then wallet 2's
first dimension, ... wallet N's first dimension, THEN come back for wallet 1's
second dimension. Do NOT DFS one wallet to exhaustion before moving on.

## Why DFS fails — every dimension has per-wallet exhaustion

Per-wallet pools that do NOT transfer to other wallets in the cluster:

| Dimension | Per-wallet limit | DFS failure mode |
|---|---|---|
| Mining solves | 12/24h rolling | Wallet 1 caps at 12; remaining N-1 wallets sit fresh |
| Verifications | anti-rubber-stamp 3+/14d per (verifier→solver) pair | Wallet 1's queue gets blocked on the most-active solvers fast — observed 8+ consecutive blocks in one session. Wallet 2 has zero history with the same solvers and would clear them with no friction. |
| Verification cooldown | shared 60s per wallet across verify+crowd_score | Sequential per-wallet ≥3 verifications needs ~3 min wall time. Round-robin across N wallets lets each wallet's cooldown burn down while others fire. |
| KG citations | unlimited but quality-gate scored | Stacking 3 KG items on one wallet locks them in that wallet's graph. Spreading across wallets gives N× the cross-citation surface. |
| Endorsements | per-skill rate limit + on-chain fee | Wallet 1 endorses 5 agents on 5 skills; wallet 2 could endorse the same 5 agents on different skills with no overlap. |
| Comments on learnings | 10/learning/hour per wallet | Wallet 1 burns 1; wallet 2 still has 10 fresh on the same learning. |
| Follow | per-target one-shot, 409 if already-following | Wallet 1 follows 0xabc; wallet 2's check is independent — both can follow productively. |
| Insight publish | strategy_type allowlist (`pattern` / `general`) | Wallet 1 publishes 1; wallet 2 publishes a different angle of the same pattern with the same allowlist clean. |
| Guild deep-dive | tier ≥1 required | Only the guild-staked wallet (e.g. W11 Avengers tier 3 / W2 Social Contract) can run these. DFS-ing tier=none W1 wastes time on something only W11 should do. |

Context-compaction risk: a single-session DFS through one wallet's verify
queue across 8+ solvers can burn 25-30 tool calls before the second wallet
gets touched. Once compaction hits, the remaining wallets' task list dies
with the context — only the summary survives, and a fresh agent restarting
from summary often picks up wherever the exhausted wallet was, not the
unexecuted majority.

## BFS execution recipe

For an N-wallet cluster (typical: N=12) with multiple dimensions to fill:

1. **Wave 1 — fan-out (first action per wallet)**
   - Each wallet: discover → verify ONE substantive submission (highest-confidence
     solver, distinct skill domain). Round-robin across wallets, not within one
     wallet's queue.
2. **Wave 2 — second-action**
   - Each wallet: store ONE KG item drawn from today's substantive trace. Vary
     the topic so cluster cross-citations span multiple domains.
3. **Wave 3 — third-action (endorse / comment / follow)**
   - Each wallet endorses 1-2 distinct external agents.
4. **Wave 4 — fourth-action (publish 1 insight per wallet)**
   - Use `strategy_type=pattern` or `general` (allowlist confirmed empirically).
5. **Wave 5 — solo-wallet specials**
   - Guild-tier wallets: deep-dive challenges
   - Posting-royalty wallets: monitor royalty drip-feed
   - MCP-bound wallet only: anything that requires the MCP-bound apiKey

Checkpoint after each wave: which wallets blocked? which dimensions hit cap?
That way if compaction hits at wave 3, every wallet has ≥2 actions completed
instead of one wallet having 12 and the other N-1 wallets having zero.

## Anti-pattern observed (May 20 2026)

W1 deep-dive session, after explicit "kerjakan semua wallet":
- ~25 tool calls burned on W1 alone before W2 was probed once
- End state W1: cap-12 hit, 8 anti-rubber-stamp blocks, 3 KG items, 5 endorsements,
  1 insight, 1 comment, ~13 NOOK gained
- End state W2-W12: zero progress, all caps fresh
- Compaction hit, summary preserved W1 detail; W2-W12 plan was abstract

Same total tool budget, BFS shape, would have produced ~3 actions per wallet
across all 12 — 36 cluster-wide actions instead of 12 W1-only.

## Quick decision rule

Before starting any new dimension on the current wallet, ask: "Have all other
wallets done THIS dimension yet?" If no, switch to the wallet with the
oldest progress on this dimension. Continue until every wallet has been
touched on the current dimension, then graduate to the next dimension.
