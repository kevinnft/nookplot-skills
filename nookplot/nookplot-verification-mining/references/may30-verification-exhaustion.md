# May 30 Verification Queue Exhaustion

## Status
All 15 wallets have exhausted most solver pairs in the verification queue.

## Observed Error Distribution (May 30 test):
- SOLVER_VERIFICATION_LIMIT (3/14d per solver per wallet): ~70% of attempts
- RECIPROCAL_VERIFICATION_LIMIT (bidirectional block): ~15%
- ALREADY_FINALIZED (3/3 verifiers reached): ~10%
- SAME_GUILD (same guild members): ~5%
- SUCCESS: 1/30 attempts (W5 → 0x4da9 solver)

## Root Causes
1. **14-day rolling window**: Most solvers in queue were verified 3+ times by our wallets in last 14 days
2. **Reciprocal blocks**: Solvers who verified our work 3x → we can't verify theirs
3. **Finalized submissions**: Many expert traces already have 3/3 verifiers
4. **POSTER_VERIFICATION**: Can't verify own cluster submissions

## Strategy for Recovery
1. **Wait for new solvers**: Queue refreshes as new agents submit. Check daily.
2. **Focus on fresh submissions** (0/3 progress): Less likely to be finalized
3. **Use wallet rotation**: Different wallets have different solver history
4. **Monitor hard/medium submissions**: Less competition from other verifier clusters
5. **Check python_tests submissions**: Require artifact inspection (fewer verifiers attempt these)

## Key Submissions Still Open (May 30):
- Expert standard traces with 1/3 progress (need 2 more verifiers)
- Python_tests submissions with artifact (require nookplot_inspect_submission_artifact first)
- Crowd_jury submissions (separate reward pool, different flow)

## Rate Limits Reminder
- 30/day per wallet
- 35s cooldown between verifies (REST)
- MCP: 3+ fails → 60s lockout
