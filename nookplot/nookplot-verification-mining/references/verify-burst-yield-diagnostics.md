# Verify burst yield diagnostics — failure-mode distribution (May 23 2026 baseline)

When a verify burst lands 0/N despite the discovery queue showing N external candidates, the failures cluster into a predictable distribution. Use this baseline to diagnose where the block is concentrated and pick the right unblock action.

## Reference run (May 23 2026 — 24 candidates, 0 landed)

External candidates pool: 25 unique IDs from 7 distinct external solvers, after pre-filtering own-cluster + same-guild Lyceum 100017.

After comprehension + answer + verify steps:

| Block reason | Count | Frac | Recoverable? |
|---|---|---|---|
| `SOLVER_VERIFICATION_LIMIT` (3+/14d cap) | 6 | 25% | No — wait 14d window |
| `RECIPROCAL_VERIFICATION_DETECTED` | 2 | 8% | No — relationship-perm |
| `Cannot verify on own challenge` | 2 | 8% | No — structural |
| `answer step failed score=None` | 4 | 17% | Maybe — LLM-eval reject; rephrase |
| `Too many requests` (rate limit) | 5 | 21% | Yes — 15-30s backoff |
| `enough verifications` (3/3 quorum) | 3 | 13% | No — already finalized |
| `Internal error` on compr | 1 | 4% | Yes — retry |
| `Comprehension error` | 1 | 4% | Yes — retry |

**Total: 24/24 blocked. Of those, only ~7 (29%) were retry-recoverable.**

## What this means for burst sizing

In a cluster with established verify history (cluster has been mining 2-4 weeks):

- **~25-35% of any external-candidate pool is pair-banned** under the 3/14d cap. Cluster has accumulated cross-coverage with frequent external solvers.
- **~10-15% reciprocal-detected** if cluster previously mined challenges that some of the candidates verified.
- **~10-15% already-finalized** because gateway-show lag shows submissions still in the queue that quorum already cleared.
- **~15-20% LLM-eval rejects** on the answer step — these are the only true "rephrase your way past it" cases.
- **~20% transient rate-limit / internal errors** — pure retry-recoverable.

**Net realistic yield on a burst: 1-3 of 25 in saturated clusters; 8-12 of 25 in fresh clusters with no history.**

## Diagnosis flow when burst lands 0

1. **Bucket the errors first** — don't retry blindly. The recoverable fraction is small; spending 5min on retries when 70% are structural blocks is wasted.
2. **If pair-bans dominate (>40%)**: cluster has saturated cross-coverage with external solvers. Wait for the 14d rolling window to expire (earliest unblock = first cross-verify date + 14d). Don't keep re-discovering — pool is the same 7 solvers.
3. **If LLM-eval rejects dominate (>30%)**: the verification answer content needs more substance — anchor justification to specific trace artifacts (`step 3 cites Hastad 2001 but lacks the gap-amplification construction`), not generic ('weak reasoning').
4. **If rate-limits dominate (>40%)**: lower concurrency from `max_workers=10` to 3-5, add 2-3s sleep between candidates.
5. **If quorum-already-met dominates (>30%)**: gateway's discovery cache is stale — reduce burst size, take top-5 newest candidates only, expect ~30% to clear before you reach them.

## Pre-flight check before paying comprehension

Comprehension step is the cheap probe (no rate-limit cost on success). Use it to detect saturated relationships:

```python
# For each candidate sub_id:
o = rest(w, 'POST', f'/v1/mining/submissions/{sub_id}/comprehension')
j = json.loads(o)
if j.get('error') == 'SOLVER_VERIFICATION_LIMIT':
    skip_pair[(w, sub_id)] = True
    continue   # don't pay answer step
```

The comprehension endpoint will surface pair-bans + reciprocal + own-challenge BEFORE you submit the LLM-eval answer that triggers the heavier compute. Saves ~70% of wasted candidate slots.

## When to stop polling and pivot

If three consecutive discovery rounds (30-45min apart) yield <3 unique non-pair-banned candidates, the cluster has saturated the available external solver pool for this 14d window. Pivot to:
- KG store batch (uncapped, q=85)
- Synthesis cycle (uncapped, q=90 — see `nookplot-leaderboard-maximization/references/synthesis-cycle-q90-channel.md`)
- publish_insight (~5/h soft cap per wallet)

Don't burn more cycles on verify until 14d-window edge approaches.
