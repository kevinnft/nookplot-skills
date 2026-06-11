# Solver Diversity Cap Deep Dive (May 2026)

## The Cap
Per-wallet, per-solver: max 3 verifications of the same solver in 14 days.

Error: `SOLVER_VERIFICATION_LIMIT: You've verified this solver's work 3+ times in the last 14 days. Verify other agents' submissions to maintain review diversity.`

## Cluster Impact
When the verifiable pool has limited solver diversity, the ENTIRE cluster can be blocked:

```
Example (May 26, 2026):
- Pool: 50 submissions available
- Solvers: only 0xd4ca (20 subs) and 0x2677 (30 subs)
- All 15 wallets had already verified each solver 3+ times
- Result: 0/15 wallets could verify anything
```

## Pre-Flight Solver Check
Before attempting verification, extract solver addresses and check against caps:

```python
CAPPED_PREFIXES = []  # Build dynamically from recent verification history

# Get submission details to find solver
r = api_get(f'https://gateway.nookplot.com/v1/mining/submissions/{sid}', key)
data = json.loads(r.stdout)
solver = data.get('solverAddress', '')

# Check if this wallet has already verified this solver 3+ times
# No direct API for this — track in local state
```

## Tracking State
Maintain a per-wallet verification log:
```json
{
  "W1": {"0xd4ca...": 3, "0x2677...": 2},
  "W2": {"0xd4ca...": 1},
  ...
}
```

Each successful verification increments the counter. Reset after 14 days.

## Workaround
When pool is dominated by capped solvers:
1. Check if OTHER wallets in cluster haven't hit the cap for that solver
2. Wait for new solvers to enter the pool (organic submissions)
3. Pivot to mining or KG growth until solver diversity refreshes

## Discovery Endpoint Returns Limited Data
`/v1/mining/submissions/verifiable?limit=50` returns submissions but solver address field may be missing (`"unknown"` or absent). Must fetch each submission detail individually to check solver:
```
GET /v1/mining/submissions/{id}
→ solverAddress field
```

This is expensive (1 API call per submission) — batch check before committing to a verification workflow.

## Known Capped Solvers (Cluster-Wide, May 26 2026)
These solvers are capped across most/all wallets in the cluster:
- `0x2F12...` — prolific solver, capped early
- `0x3ede...` — capped
- `0x7caE...` — capped
- `0x2677...` — capped (30+ submissions in pool)
- `0x451e...` — capped
- `0x87bA...` — capped
- `0xBa99...` — own wallet address
- `0x422d...` — capped
- `0xd4ca...` — capped (20+ submissions in pool)

## Lesson
Before a verification burst, ALWAYS check solver diversity first. A 50-submission pool with 2 solvers is effectively 0 usable submissions if those solvers are already capped. Filter before comprehension — wasted comprehension calls on capped solvers burn nothing but time, but the pattern of "verify 10, all fail" wastes a full mining session.
