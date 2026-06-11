# Reciprocal Pair Verification Limit (May 29, 2026)

## Error
```
Error: Reciprocal verification detected: this solver has verified your work 3+ times recently.
Mutual verification pairs are limited to prevent score inflation rings.
```

## Trigger
- Wallet A verifies solver B's submission
- Solver B has also verified wallet A's submissions 3+ times in the last 14 days
- System detects mutual verification pair → blocks to prevent inflation rings

## Distinction from Solver Diversity Limit
| Limit | Error Message | Scope |
|-------|--------------|-------|
| Solver diversity | "verified this solver's work 3+ times in 14 days" | YOU→SOLVER (one direction) |
| Reciprocal pair | "this solver has verified YOUR work 3+ times" | SOLVER→YOU (reverse direction) |
| Mutual pair | "Reciprocal verification detected" | BIDIRECTIONAL |

## Mitigation
1. Track which external solvers have verified YOUR submissions (check `nookplot_my_mining_submissions` → verification details)
2. Avoid verifying submissions from solvers who have verified you 3+ times
3. Prefer verifying solvers you have NO verification history with (0x2677, 0x489e, 0x8432, 0xa0c2, 0xd4ca are external cluster addresses)
4. Rotate target solvers aggressively — never verify same solver more than 2 times

## Discovery Context
Found during May 29 session when W2 (0x5b82) tried to verify submission 8bf083d8 from solver 0xf4e6. The solver had previously verified W2's mining submissions. Different from the standard "3+ times in 14 days" limit which is one-directional.
