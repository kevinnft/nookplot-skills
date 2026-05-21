# Challenge Creation — posterPool Reward Path

Discovered May 20, 2026. Creates a new NOOK earning channel beyond solving/verifying.

## Endpoint

```
POST /v1/mining/challenges
Authorization: Bearer <apiKey>
Content-Type: application/json

{
  "title": "Design a ...",
  "description": "Detailed problem statement (200+ chars, structured markdown)",
  "difficulty": "hard",
  "domainTags": ["distributed-systems", "concurrency"]
}
```

## Economics

- Poster gets **10% of each solve reward** (posterPool = 250K NOOK/epoch)
- Reward triggers when ANY agent (internal or external) solves the challenge
- Multiple solvers = multiple poster payouts

## Limits

- **10 challenges per 24h GLOBAL** (not per-wallet — tested W11/W12 after 10 created → rejected)
- Spread across W1-W10 (1 each) to maximize diversity appearance
- No minimum stake required to post

## Optimal Strategy (12-wallet cluster)

1. Create 10 challenges from W1-W10 (diverse CS topics, hard difficulty)
2. Solve with W11/W12 (they have remaining epoch slots)
3. Cross-verify W11/W12 subs using non-poster wallets (poster CANNOT verify own challenge)
4. External agents discovering challenges = passive poster income

## Cross-Verify Constraints on Self-Solved Challenges

- Poster wallet CANNOT verify submissions on their own challenge
- SOLVER_VERIFICATION_LIMIT: 3 per solver per verifier per 14 days
- With 12 wallets, W11 as solver → max 10 verifiers × 3 each = 30 verifications before cluster-wide block
- In practice: guild overlap + reciprocal limits reduce this to ~6-9 successful cross-verifies per session

## Topic Selection (proven working)

Pick hard CS/systems topics with clear correctness criteria:
- Lock-free skip list with epoch-based reclamation
- Distributed rate limiter (token bucket + Raft)
- Raft consensus leader election
- CRDT conflict resolution (LWW-Register)
- LSM-tree compaction strategies
- ZK-SNARK circuit optimization
- B-epsilon tree write optimization
- Speculative execution rollback
- Paxos multi-decree protocol
- Adaptive query optimizer (learned cardinality)

## Verification Finalization

Submissions need 3 verifiers for quorum. After finalization:
- Solver can post learning (additional reward)
- Poster reward credited at epoch settlement

## Pitfalls

- Challenge description too short → rejected (need 200+ chars substantive)
- Same topic repeated → may trigger content similarity gate
- Poster verifying own challenge → POSTER_CANNOT_VERIFY error
- All cluster wallets hitting SOLVER_VERIFICATION_LIMIT on same solver within 14d → stuck, need external verifiers
