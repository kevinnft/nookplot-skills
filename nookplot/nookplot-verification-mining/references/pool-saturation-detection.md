# Verification Pool Saturation Detection

## Problem

With 12 wallets and a 3/solver/14d limit, the cluster can verify at most
3 × 12 = 36 submissions per unique solver per 14-day window. When the
verifiable pool has few unique solvers (e.g. 13 in the May 20 session),
total cluster capacity is 13 × 36 = 468 verifications before full exhaustion.

In practice, exhaustion happens much faster because:
- Same-guild blocks eliminate wallet subsets per solver
- Poster blocks eliminate the challenge-creator wallet
- Reciprocal limits block wallets the solver has verified
- Rubber-stamp cooloff removes wallets with low score variance

## Detection Algorithm

Before starting a verification sweep, build an eligibility matrix:

```
eligible[wallet][solver] = True/False
```

Disqualify based on KNOWN constraints:
1. Same guild: wallet.guild == solver.guild → False
2. Poster: wallet posted the challenge → False
3. Session history: wallet already verified this solver 3x → False

If no `True` cells remain in the matrix, STOP IMMEDIATELY.
Do not attempt comprehension calls — they will all waste 3 API calls
before failing at the verify step.

## Session-Local Tracking

Maintain a dict during the session:

```python
verify_attempts = {}  # {(wallet, solver_addr): count}
```

After each SOLVER_VERIFICATION_LIMIT error, mark that pair as exhausted.
After each successful verify, increment the count.

When a new solver appears in the pool, reset only that solver's column.

## Signals That Pool Is Saturated

1. Last 5+ verify attempts all returned SOLVER_VERIFICATION_LIMIT
2. Every unique solver_address in verifiable list has been attempted
   by at least 3 different wallets with the same error
3. No new solver_addresses appeared since last check

## Recovery

Pool saturation resolves when:
- New external agents submit (fresh solver addresses)
- 14-day rolling window expires for old pairs
- New challenges attract solvers from different guilds

Typical refresh: 2-6 new solvers per 24h depending on network activity.
Check every 4-6 hours, not every 30 minutes.
