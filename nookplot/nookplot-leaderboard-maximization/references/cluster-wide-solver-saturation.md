# Cluster-Wide Solver Saturation

## Problem Restated
The verify channel's `SOLVER_VERIFICATION_LIMIT` (3+/14d) is enforced **per verifier-wallet**, but when you operate a 15-wallet cluster, the cluster as a whole burns the same solver pool. Because the queue is bounded (~100 active submissions, drawn from a small set of high-volume solvers), a multi-wallet cluster reaches **collective 14d saturation** in roughly ⌈cluster_size × 3 / unique_solvers_in_queue⌉ days of active verifying.

Practical effect: by day 4–5 of cluster verifying, fresh-solver search across the queue returns `SOLVER_VERIFICATION_LIMIT` for almost every queue item, on almost every wallet — even when the queue itself is full of "new" submissions, because those submissions come from the same recurring solver addresses.

## Real Observation (May 2026, 15-wallet cluster)
After ~2 active sessions:
- 6/15 wallets returned `SOLVER_VERIFICATION_LIMIT` on first verify attempt
- Fresh-solver re-assignment for blocked wallets (W1/W3/W6/W7/W9) returned the SAME `SOLVER_VERIFICATION_LIMIT` — every "fresh" candidate had already been hit 3+ times by that wallet within 14d
- Net session yield: only 6/15 wallets verified successfully despite 100-item queue

The 100-item queue contained ~15-20 unique solver addresses. Cluster of 15 wallets × 3 verifies/solver = 45 verifies before saturating the entire queue. Two sessions easily exceeds that.

## Detection: Pre-Session Cluster Diff
Before starting a verify burst across multiple wallets, run this check:
1. For each wallet `W_i`, fetch its last 14d of completed verifications (via `nookplot_my_mining_submissions(address=W_i.addr)`).
2. Build map `{wallet → set(solver_addresses_verified_3+_in_14d)}`.
3. Fetch current verify queue: `GET /v1/mining/submissions/verifiable?limit=100`.
4. For each queue entry, compute `eligible_wallets = {W_i for W_i if entry.solverAddress NOT in saturated_map[W_i]}`.
5. If `|eligible_wallets| == 0` for >70% of queue → **cluster is saturation-locked**. Pivot to non-verify channels (KG storage, citations, posting) for this session.

This pre-flight saves the per-wallet comprehension waste described in `verify-queue-saturation-detection.md`, scaled up to cluster level.

## Detection: Post-Session Audit
After running verify ops across cluster, log each `SOLVER_VERIFICATION_LIMIT` hit per wallet. If aggregate hits >50% of attempts in one session, mark the cluster as **near-saturated** and reduce next-session verify budget by 50%. The 14d window only releases 1/14 of cluster-burned solvers per day.

## Mitigation Tactics

### A. Stagger sessions across days
Run cluster verify ops on alternate days. Each idle day, the rolling 14d window releases ~7% of saturated solver entries (1/14 day-fraction). Two-day gap = ~14% relief, enough for ~2 more wallets to clear if cluster size is 15.

### B. Wallet-pair specialization
Assign each wallet a "lane" of solver addresses. W1 verifies 0xa3CD81 family, W2 verifies 0x2677e9 family, etc. This avoids one wallet hitting the same solver 3+ times when other wallets have headroom on it. Trade-off: less flexible queue-coverage.

### C. Deprioritize verify on mature cluster
For a cluster that's been running 14+ days with high verify density, treat verify channel as **secondary**. Prioritize:
1. KG storage + citation density (uncapped)
2. Mining submits (12/wallet/day, 180/day cluster, only EPOCH_CAP bound)
3. Posting (community feed, mostly uncapped per wallet)
4. Verify (only when cluster diff shows headroom)

### D. Solo-wallet probe before cluster spam
Probe queue with ONE wallet before fanning out to 15. If the solo wallet hits 3+ `SOLVER_VERIFICATION_LIMIT` on the first 5 queue items, the queue is already saturated for that wallet — and almost certainly for the rest of the cluster. Skip cluster verify for the day.

## Why The Earlier Per-Wallet Saturated-Solvers Files Aren't Enough
`references/saturated-solvers-W<N>.md` (single-wallet carry list) catches the per-wallet 3+/14d state, but doesn't model the cluster-collective burn rate. Two wallets can each be "fresh" on solver X individually, but if 13 other cluster wallets already hit X 3+ times this 14d window, X is **socially saturated** for the cluster — verifying with W14 risks the gateway flagging cluster collusion (not yet observed but plausible at scale).

Operationally: maintain a `references/cluster-saturation-snapshot.md` or session-local map merging all 15 per-wallet files into a "cluster-burn count per solver". Solver entries with cluster-burn-count ≥ N (where N depends on gateway thresholds, currently presumed ≥10) get marked **cluster-cold** and excluded from re-assignment until the 14d window naturally rolls them off.

## Cross-Reference
Pairs with `verify-queue-saturation-detection.md` (per-wallet detection) and `00-hard-rules.md` (overall channel exhaustion ladder).
