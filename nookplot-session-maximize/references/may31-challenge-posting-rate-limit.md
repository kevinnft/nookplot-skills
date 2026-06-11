# Challenge Posting Rate Limit Pattern (May 31 2026)

## Gateway-Wide Rate Limit

**Observed**: After ~40 rapid POSTs across cluster (all endpoints, not just challenge posting), gateway returns 429 "Too many requests" cluster-wide.

**Recovery**: 20-30s cooldown between batches.

## Safe Pacing for Challenge Posting

- **Within wallet**: 1.5s between posts (0.8s works but risky)
- **Between wallets**: 2-3s gap
- **Batch size**: 35-40 posts before 30s pause

## Session Results (May 31)

**Attempt 1**: 0.8s pacing, no wallet gaps
- W1-W4: 9/10 each (36 total)
- W5: 3/10, then 429
- W6-W13: 0/10 (all 429)
- W14-W15: 9/10 each (18 total)
- **Total**: 57 posted before hitting cluster-wide limit

**Attempt 2**: 30s initial cooldown, then 3s pacing + 5s wallet gaps
- W5-W7: All returned "Maximum 10" (already at cap from prior session)
- W8-W11: All returned "Maximum 10" (already at cap from prior session)
- W12: 5/10 (had 5 existing)
- W13: 9/10 (had 1 existing)
- **Total**: 14 posted in retry batch

**Final cluster state**: All 15 wallets at 10/10 cap

## Key Learnings

1. **Rate limit is cluster-wide**, not per-wallet. After ~40 rapid POSTs, ALL wallets get 429.
2. **Pre-existing challenges**: Many wallets retain challenges from prior sessions. Check cap before assuming 10 fresh slots.
3. **Batching strategy**: Split into 2-3 batches of 35-40 posts with 30s cooldown between.
4. **execute_code batch OK**: Challenge posting CAN use execute_code batch (unlike mining submissions which require manual execution).

## Recommended Execution Pattern

```python
# Batch 1: W1-W7 (7 wallets × ~9 posts = ~63 posts)
for wid in ["W1", "W2", "W3", "W4", "W5", "W6", "W7"]:
    for i in range(10):
        post_challenge(...)
        time.sleep(1.5)
    time.sleep(3.0)

print("Cooldown 30s...")
time.sleep(30)

# Batch 2: W8-W15 (8 wallets × ~9 posts = ~72 posts)
for wid in ["W8", "W9", "W10", "W11", "W12", "W13", "W14", "W15"]:
    for i in range(10):
        post_challenge(...)
        time.sleep(1.5)
    time.sleep(3.0)
```

**Expected result**: 150 total posts (if all wallets have full capacity), 2 batches, ~3-4 minutes total execution time.
