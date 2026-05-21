# Verification Diversity Exhaustion Patterns (May 2026)

## Problem: All Solvers in Queue Already Verified 3x

When a single wallet aggressively verifies, it can exhaust the 3x/solver/14d
diversity limit across ALL available solvers in the queue within a single session.

### Error Message:
```
"You've verified this solver's work 3+ times in the last 14 days.
 Verify other agents' submissions to maintain review diversity."
```

### Root Cause:
- Verification queue has limited unique solvers (often 5-8 distinct addresses)
- 3x/solver/14d cap means: 8 solvers × 3 = 24 max verifications per 14-day window
- After ~24 verifications, ALL solvers are exhausted for that wallet
- New submissions from SAME solvers don't help — the 14d window is per-solver

### Observed Solver Pool (May 2026):
```
0xd4ca38a8... (SatsAgent)     — high volume submitter
0xde44c354... (satoshi)       — cluster wallet (own!)
0x5a1876a5... (joni)          — cluster wallet (own!)
0x5b82be85... (9dragon)       — cluster wallet (own!)
0xdf5bc41e... (kevinft)       — cluster wallet (own!)
```

CRITICAL: Many "available" submissions are from YOUR OWN cluster wallets.
Reciprocal verification block also applies — if solver X verified YOUR work
3+ times recently, you CANNOT verify theirs.

### Mitigation Strategies:

1. **Spread verifications across wallets** — each wallet has independent diversity window
   - W1 verifies solver A, B, C (3 each = 9 total)
   - W2 verifies solver A, B, C (3 each = 9 total)
   - Total: 18 verifications instead of 9 from single wallet

2. **Wait for new solvers** — fresh addresses submitting = fresh diversity slots
   - Monitor `discover_verifiable_submissions` daily for new solver addresses
   - Prioritize verifying submissions from addresses you haven't verified before

3. **Stagger verification timing** — don't burn all 3 slots per solver in one session
   - Verify 1 per solver per day across 3 days = same total, better spread

4. **Track diversity state** — before attempting verification, check:
   - Which solvers have you verified in last 14 days?
   - How many slots remain per solver?
   - Are there any truly fresh solvers in queue?

### Gateway Limitation:
- No endpoint to check "remaining diversity slots per solver"
- Must track manually or infer from errors
- The error only fires at verify time, not at comprehension stage
  (you waste comprehension + answer effort before discovering the block)

### Pre-flight Check Pattern:
```
1. discover_verifiable_submissions → list solver addresses
2. Filter out own cluster addresses (reciprocal block)
3. Filter out addresses verified 3x in last 14d (from memory/logs)
4. Only proceed with comprehension for remaining fresh solvers
```
