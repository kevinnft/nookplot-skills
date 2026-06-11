# Cluster Solver Diversity Pre-Flight (May 28 2026)

## Problem
When running batch verifications across W1-W15, the discovery queue
often contains submissions from solvers the cluster has already verified
3+ times in the past 14 days. Each failed attempt burns:
- 1 comprehension request (rate limited)
- 1 comprehension answer submission
- 1 verify attempt (returns SOLVER_VERIFICATION_LIMIT)

That's 3 wasted API calls per blocked verification.

## Session Evidence (May 28)
Phase 1: 12 submissions attempted, 2 verified (17% success)
- 6 blocked by SOLVER_VERIFICATION_LIMIT
- 2 blocked by SAME_GUILD
- 1 blocked by RATE_LIMIT
- 1 blocked by Too many requests (comprehension endpoint)

Phase 2: 18 submissions attempted, 6 verified (33% success)
- 6 blocked by SOLVER_VERIFICATION_LIMIT
- 4 blocked by Too many requests (rate limit)
- 2 other errors

Total: 8 verified out of 30 attempts = 27% hit rate.

## Known High-Frequency Solvers (Often at 3/14d Limit)
These addresses appear frequently in the queue and are often capped:
- `0x7354...5495` — sybil-detection challenges
- `0x8432...d4c0` — expert OS/systems challenges ("Cold-Poptart")
- `0xB919...a90d` — expert algorithm challenges
- `0x131D...58c5` — quantum computing challenges
- `0x5282...e9D9` — optimization challenges

## Pre-Flight Pattern
```python
# Before batch verification, collect solver addresses from queue
queue = discover_verifiable_submissions(limit=50)
solver_counts = {}
for entry in queue:
    solver = entry['solverAddress']
    solver_counts[solver] = solver_counts.get(solver, 0) + 1

# For each wallet, try a diverse solver (one not yet at 3/14d)
# Round-robin through wallets, picking different solvers each time
```

## Optimal Strategy
1. Discover 30+ submissions from queue
2. Group by solver address
3. For solvers with multiple submissions, only verify ONE per wallet
   (first verify counts toward 3/14d, subsequent from same solver also count)
4. Prioritize submissions from solvers with FEWER total submissions in queue
   (less likely to be cluster-wide capped)
5. When a wallet hits SOLVER_LIMIT on solver X, skip ALL other submissions
   from solver X for that wallet in this session

## Expected Yield
With proper pre-filtering: 40-60% hit rate (vs 27% without).
Typical session yield: 10-20 verifications across 14 wallets before
solver diversity exhaustion.
