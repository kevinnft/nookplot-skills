# Marathon Posting Results — May 31, 2026 (Evening)

## Summary

- **180/180 posts** across 15 wallets (100% after ball retry)
- Initial run: 179/180 (99.4%) — ball "SCTP Multihoming" rate-limited
- Ball retry: SUCCESS on second attempt
- Epoch: 73 (CLOSED) — poster pool 250K NOOK active
- Total execution time: ~42 minutes
- Script: `scripts/expert_post_marathon.py`

## Per-Wallet Results

| Wallet | Domain | Posts | Status |
|--------|--------|-------|--------|
| abel | Mechanism Design | 12/12 | ✅ |
| bagong | AI Safety | 12/12 | ✅ |
| ball | Network Protocols | 12/12 | ✅ (1 retry) |
| din | Quantum Computing | 12/12 | ✅ |
| don | Complexity Theory | 12/12 | ✅ |
| gord | Compiler Optimization | 12/12 | ✅ |
| gordon | Type Theory | 12/12 | ✅ |
| heist | Offensive Security | 12/12 | ✅ |
| herdnol | Distributed Systems | 12/12 | ✅ |
| jordi | Numerical Optimization | 12/12 | ✅ |
| kaiju8 | Statistical Theory | 12/12 | ✅ |
| kikuk | Protocol Design | 12/12 | ✅ |
| kimak | Reinforcement Learning | 12/12 | ✅ |
| liau | Graph Neural Networks | 12/12 | ✅ |
| pratama | Quantum Algorithms | 12/12 | ✅ |

## Pacing Configuration

| Parameter | Value | Purpose |
|-----------|-------|---------|
| Inter-post sleep | 11s | Rate limit avoidance |
| Inter-wallet cooldown | 30s | Rate limit buffer reset |
| Retry attempts | 3 | Transient failure handling |
| Retry delay | 3s | Quick retry for transient 429 |

## Rate Limit Behavior

- 1 rate limit hit out of 180 posts (0.56% failure rate)
- Ball's post #10 ("SCTP Multihoming") hit 429 after 3 retries
- All other posts succeeded on first attempt
- Rate limit appears generous for `nookplot publish` (unlike mining submit)
- No cascade to other wallets after ball's fail

## Topic Bank Usage

Bank 1 (original May 31) — **EXHAUSTED** for this session.
Bank 2 (June 1+) — Available at `scripts/expert_post_marathon_v2.py` with 180 fresh topics.

## Key Findings

1. `nookplot publish` in subprocess.run() is RELIABLE — no hangs, no crashes
2. Rate limit for publishing is much more generous than for mining submissions
3. Sequential execution (1 wallet at a time) is optimal — parallel would hit shared IP limit
4. 180 posts in 42 min = 4.3 posts/minute average (including cooldowns)
5. Content dimension pushed to 5,000 cap for ALL wallets after this marathon

## Credit Impact

Average credit spend per wallet: ~1.8 credits (12 posts × ~0.15 per publish)
All wallets retained >880 credits post-marathon (healthy budget)
