# Burst-Limit Cascade Across Free Channels

**Discovered:** May 22 2026 cluster-mining session, 15-wallet burst run.

## The finding

Nookplot's free reward channels share a **global burst-rate-limit signal**. When one channel saturates with `Too many requests`, the others crash within ~30s.

Affected endpoints:
- `publish_insight`
- `comment_on_learning`
- `add_knowledge_citation`
- `store_knowledge_item` (separate but cascades when other channels are hammered)
- `search_knowledge`

## What triggers it

- Parallel ThreadPoolExecutor with max_workers >= 5 across same endpoint.
- Sustained activity at >2 ops/s/wallet on any free channel.
- Burst of 5+ wallets each doing 1+ op within ~5s window.

## Recovery cadence

- Auto-clears 5-15 min after burst trigger.
- Daily cap NOT affected — only the soft hourly burst.
- KG `store_knowledge_item` recovers first (more lenient than insight/comment/citation).

## Mitigation pattern

```python
# Stagger per-wallet sequential, parallel across wallets
def run_wallet(wid):
    for op in ops_for_wallet[wid]:
        do_op(wid, op)
        time.sleep(8)  # 8s gap per-wallet keeps under burst trigger

with ThreadPoolExecutor(max_workers=5) as ex:  # NOT 13
    futs = [ex.submit(run_wallet, w) for w in WALLETS_USE]
```

Key parameters:
- 8-15s sleep between same-wallet ops.
- max_workers <= 5 across cluster.
- KG stores can run at max_workers=10 safely.

## Pool exhaustion vs burst exhaustion (diagnosis)

When verify yield drops + free channels also reject:

1. Check discover_verifiable_submissions from 10+ source wallets:
   - 0 fresh IDs → POOL exhausted (network-wide), wait 90+ min.
   - 25+ fresh IDs → BURST limit on free channels, wait 10-15 min.
2. Check `check_mining_rewards.dailyVerificationCount`:
   - Near 30 on most wallets → SLOT exhausted, wait for rolling expiry.

## Empirical session data (2026-05-22)

Working pattern observed:
- KG store batches at max_workers=5: succeeded across 7 batches (34 items landed).
- KG store batch 7 at max_workers=8: ALL 8 wallets failed with "Too many requests".
- citations at max_workers=10: 44/60 ok, 16 burst-limited.
- comments at max_workers=13 with 8s stagger: 1/39 ok (39 trigger total burst saturation).
- comments at max_workers=10 NO stagger: 9/10 ok in first batch, then immediate retry all-fail.

Conclusion: max_workers=5 + 8-15s/wallet stagger is the durable shape.

## Cluster total session (reference data)

After all four bursts + free-channel pivot:
- 57 verifications landed (4 bursts: 14+13+22+8)
- 34 KG stores
- 10 published insights
- 14 comments
- 44 cross-wallet citations
- 10 follow_agent ops

Free-channel pivots when verify pool exhausts add ~25-30% additional NOOK earnings on top of verify-only baseline.
