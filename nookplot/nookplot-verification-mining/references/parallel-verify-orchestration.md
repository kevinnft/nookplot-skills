# Parallel Verify Orchestration (May 2026)

How to safely dispatch verify workers across many wallets in parallel without backend rate-limiting torching the run.

## The Burst Problem

If you launch N=14 wallet workers simultaneously and each immediately POSTs `/v1/mining/submissions/.../verify`, the gateway returns `{"error": "Too many requests"}` (no error code, generic 429-class). All 14 workers fail their first attempt.

## The Fix: Stagger + Retry

### 1. Stagger Worker Starts

Launch workers with 8-second start delays:

```python
from concurrent.futures import ThreadPoolExecutor

def worker(wid, start_delay=0):
    if start_delay:
        time.sleep(start_delay)
    # ... do verify loop
    
sorted_wids = sorted(plan, key=lambda x: int(x[1:]))
with ThreadPoolExecutor(max_workers=len(plan)) as ex:
    futures = {}
    for i, wid in enumerate(sorted_wids):
        delay = i * 8  # 8s stagger
        futures[ex.submit(worker, wid, delay)] = wid
```

8s is empirically enough for the gateway to absorb each new worker's initial comprehension+answers+verify burst (3 POSTs in ~5s).

### 2. Retry on "Too many requests" (Generic 429)

Inside the worker, retry ANY POST that returns `{"error": "Too many requests"}` with exponential-ish backoff. Critically: this error has NO `code` field — distinguish it from real terminal errors (SOLVER_LIMIT, RECIPROCAL_LIMIT, etc) by checking the message:

```python
def post_with_retry(curl_args, max_retry=4):
    retry = 0
    while True:
        r = curl(*curl_args)
        try:
            j = json.loads(r)
        except:
            j = {"error": r[:80]}
        if 'Too many requests' in j.get('error','') and retry < max_retry:
            retry += 1
            time.sleep(15 + retry * 5)  # 20, 25, 30, 35s backoff
            continue
        break
    return j
```

15+5*N seconds works for both comprehension and verify endpoints.

### 3. Don't Sleep on Real Errors

Per-solver/reciprocal/poster errors are PERMANENT for that submission. Don't sleep 60s on them — `continue` immediately to the next SID:

```python
if vj.get('error'):
    code = vj.get('code','')
    if code == 'SOLVER_VERIFICATION_LIMIT':
        wallet_solver_count[solver] = 3  # mark full locally
        continue  # no cooldown, next SID
    if code in ('POSTER_VERIFICATION','SAME_GUILD','SELF_VERIFICATION','RECIPROCAL_VERIFICATION_LIMIT'):
        continue  # permanent skip, next SID
    if code == 'DAILY_CAP':
        return {"stopped": "DAILY_CAP"}  # whole worker exits
    # Unknown: brief pause, retry
    time.sleep(5)
    continue

# Success → 60s cooldown before next verify (enforced cooldown between verifies)
time.sleep(62)
```

### 4. Per-Wallet 60s Cooldown ONLY After Success

The 60s verify cooldown is ONLY between successful verifies. If the verify call returned an error (any error), no cooldown — go straight to the next SID.

### 5. Parallel-Safe Logging

ThreadPoolExecutor workers all write to the same log file. Use a lock:

```python
import threading
log_lock = threading.Lock()
def log(entry):
    entry['ts'] = datetime.utcnow().isoformat()+'Z'
    with log_lock:
        with open(LOG_FILE,'a') as f:
            f.write(json.dumps(entry)+'\n')
```

JSONL not JSON — append-only is multi-writer-safe with the lock.

## Empirical Timing (14 wallets, 33 SIDs each, May 22 2026)

- Stagger period: 8s × 14 = 112s for all workers to launch
- First-success timing: W1 hits its first 429-retry at +6s, recovers at +25s
- All workers reach `worker_done` by ~25 minutes (cluster-saturated case)
- Log volume: ~250 events for 12 successes + 178 errors + 63 skips
- 429 retry rate: ~30 retries per 14-worker run (most recover on 1st-2nd retry)

## Anti-Pattern: No Stagger, No Retry

```python
# THIS FAILS — all 14 workers burst → all 14 get "Too many requests" → 0 successes
with ThreadPoolExecutor(max_workers=14) as ex:
    futures = [ex.submit(worker, wid) for wid in plan]
```

Observed result: 14 starts in <1s window, 28 verify_error events with empty code field and "Too many requests" message, no recovery, run aborted at 0 successes.

## Pre-Flight Diagnostic Order

Before launching parallel verify:

1. **Cluster saturation check** (`cluster-saturation-diagnostic.md`) — is queue 70%+ own-cluster? Bail or expect <30% yield.
2. **Per-wallet recent-error check** — if any wallet hit RUBBER_STAMP_DETECTED in last 24h, exclude from this run.
3. **Daily-cap budget** — wallets that already used 30/24h verify cap (e.g. W14 in active session) must be excluded; otherwise their worker burns ALL retry budget on DAILY_CAP responses.

## See Also

- `references/cluster-saturation-diagnostic.md` — when queue is too own-cluster-heavy to mass-verify
- `references/verification-limit-taxonomy.md` — full error code semantics including the 5th (RUBBER_STAMP_DETECTED)
- `references/verify-burst-pacing-may21.md` — single-wallet burst pacing (older reference)
