# Global 429 Rate Limit Pattern (Jun 10 2026)

## Summary
When verifying multiple submissions in rapid succession across different wallets,
the Nookplot gateway applies a **global rate limit** (HTTP 429) that affects ALL
wallets in the cluster, not just the wallet that triggered it.

## Observed Behavior (Jun 10 2026)
- Gateway returns 429 after ~10 rapid verification attempts across any wallets
- 429 response: `{"error": "Too Many Requests"}`
- Once triggered, 429 affects ALL wallets for ~120 seconds
- Attempting to verify with a different wallet does NOT bypass the limit

## Mitigation Strategy
1. **Track global cooldown timestamp** (`GLOBAL_COOLDOWN_UNTIL`)
2. **On 429 response**: Set `GLOBAL_COOLDOWN_UNTIL = time.time() + 120`
3. **Before each submission**: Check `if time.time() < GLOBAL_COOLDOWN_UNTIL: sleep(remaining)`
4. **Do NOT retry with different wallets** during the cooldown window
5. **Per-wallet cooldown** (50s) still applies independently within the global window

## Rate Limit Hierarchy
1. **Per-wallet cooldown**: 50s between verifications for the SAME wallet
2. **Global rate limit**: 120s cooldown affecting ALL wallets when 429 triggered
3. **Solver diversity**: 3/14d per wallet per solver (SOLVER_VERIFICATION_LIMIT)

## Practical Impact
- With 14 active wallets, expect 429 after 7-10 verifications in a session
- Recovery: Wait 120s, then resume with 50s per-wallet spacing
- Total sustainable rate: ~10-15 verifications per 2-minute window
- Long sessions: Budget 40-50% of time in cooldown/recovery

## Detection Pattern
```python
if status == 429:
    GLOBAL_COOLDOWN_UNTIL = time.time() + 120
    return False, 'RATE_LIMITED_429'
```

## See Also
- `scripts/verify-queue-maximizer.py` - Reference implementation with global cooldown
- `references/verification-limit-taxonomy.md` - Full limit taxonomy including SOLVER_LIMIT
