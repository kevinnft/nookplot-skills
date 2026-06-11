# 100%-Own-Cluster Verify Pool Saturation — May 23 2026

When a cluster (15 wallets, single guild) has many submissions in flight, the
gateway's personalized verify queue can return a pool that is **entirely** the
cluster's own work. SAFE-rule (no self-cross-verify) then yields 0 verify slots
even though every wallet sees `20 submissions need verification`.

This is a more extreme mode than the burst-cycle saturation: there the pool
held a mix and skip-rate was ~85%. Here skip-rate is 100% before pair-ban
even comes into play.

## Detection signal

```
Union pool across 15 wallets discover (limit=100 each):  42 unique IDs
After detail fetch + filter (own_cluster | same_guild | !submitted):
  Own-cluster solver:   42  (100%)
  Same-guild blocked:    0
  External candidates:   0
```

If `len(own_subs) / len(union) > 0.9` after a full sweep, you have own-cluster
saturation. The cluster's own submitted+0/3 subs have crowded out external
verifiability.

## Verify history endpoint LIES about pair-ban exposure

`GET /v1/mining/verifications?verifier=<addr>&limit=50` returned **0 items**
for every wallet, yet two attempted verifies on `solver=0x7354b0ac` failed with:

```
SOLVER_VERIFICATION_LIMIT
"You've verified this solver's work 3+ times in the last 14 days."
```

The pair-ban cache is computed against the gateway's full 14d ledger, not the
"last 50" view. Treat the verify-history endpoint as a **lower bound** on
exposure, never as authoritative for clearance.

Recipe: maintain `/tmp/verify_quota_cache.json` keyed by
`(verifier_addr, solver_addr) -> last_failure_at` and respect any entry with
`now - last_failure_at < 14d` as banned, regardless of what the history
endpoint says.

## Audit recipe (cluster preflight)

```python
# Run BEFORE planning a burst — fast, ~2 min, no verify spend
import json, subprocess, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed

with open('/home/asus/.hermes/nookplot_wallets.json') as f:
    wallets = json.load(f)
cluster_addrs = {wallets[k]['addr'].lower() for k in wallets}

GW = "https://gateway.nookplot.com"
def rest(w, method, path, body=None, t=30):
    h = ['-H', f'Authorization: Bearer {wallets[w]["apiKey"]}',
         '-H', 'Content-Type: application/json']
    cmd = ['curl', '-sS', '-X', method, f'{GW}{path}'] + h
    if body is not None: cmd += ['-d', json.dumps(body)]
    cmd += ['--max-time', str(t)]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=t+5).stdout

# Sequential per-wallet discover (rate-limit safe), 2.2s gap
elig = {}
for w in sorted(wallets, key=lambda x: int(x[1:])):
    o = rest(w, 'POST', '/v1/actions/execute',
             {'toolName': 'nookplot_discover_verifiable_submissions',
              'args': {'limit': 100}})
    if 'Too many' in o:
        time.sleep(15)
        o = rest(w, 'POST', '/v1/actions/execute', ...)
    elig[w] = set(re.findall(
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', o))
    time.sleep(2.2)

union = set().union(*elig.values())

# Rotate wallet for detail fetch (load-spread)
ws = list(wallets.keys())
own_count = ext_count = 0
for i, sid in enumerate(sorted(union)):
    w = ws[i % len(ws)]
    out = rest(w, 'GET', f'/v1/mining/submissions/{sid}')
    if 'Too many' in out:
        time.sleep(15)
        out = rest(w, 'GET', f'/v1/mining/submissions/{sid}')
    d = json.loads(out)
    if (d.get('solverAddress') or '').lower() in cluster_addrs:
        own_count += 1
    else:
        ext_count += 1
    time.sleep(0.4)

print(f'Own: {own_count} | External: {ext_count}')
# If ext_count == 0 → IDLE, no verify path available cluster-internal
```

Total wall time: ~2 min for 15 wallets + 42 details. Cost: zero verify slots.

## Action matrix (when own-cluster saturation hits)

| State | Action | Reason |
|-------|--------|--------|
| `external == 0`, sybil-rule active | IDLE, poll `discover` from 3 distinct-guild wallets every 30-45 min | Cluster cannot self-finalize; need external verifier traffic refresh |
| `external == 0` AND user demands action | PIVOT to KG `store_knowledge_item` burst (2-3 KB markdown, 4-5s sleep) — primary no-cap fallback per memory | Verify slots wasted when external pool empty; KG burst still earns reputation + citation reward |
| `external > 0` | Run cluster-batch-verify-playbook with most-constrained-first assignment | Standard path |
| `external > 0` AND every cand pair-banned | Wait for 14d window drain (track unlock_at = oldest_quota_hit + 14d) | Cluster-internal saturation cannot self-resolve |

## Polling rhythm

External sub appearance follows external-solver-traffic patterns. Empirical
from May 23 06:00 UTC observation:
- Cluster's own batch landed across W4/W5/W7/W8/W9/W10/W11/W12 ~all 0/3
- 42 own subs sat in queue
- External traffic at this hour: low (Asian afternoon / EU morning)

Recommended polling:
- 30 min during EU business hours
- 45-60 min during low-traffic windows
- One discover from W3 + W7 + W11 (cross-guild diversity sources) is enough
  to detect pool refresh; no need to hit all 15 wallets each poll

## Why "discover from saturated wallets" still helps

Even when a wallet's own verify slots are pair-banned against current pool,
its discover view samples a different gateway personalization slice.
`discover` is independent of verify eligibility — pool refresh detection
should always include all 15 wallets in the source rotation.

See: burst-cycle-may22-2026.md "Pool refresh — per-wallet discover diversity"
for the v2 → v3 → v4 pool growth pattern (93 → 112 → 140 unique IDs).
