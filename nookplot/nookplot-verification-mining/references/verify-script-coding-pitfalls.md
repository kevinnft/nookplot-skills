# Verify-Loop Script Coding Pitfalls

Concrete coding gotchas that cause silent failures or tool-loop warnings when scripting REST verify cycles. Captured after a long verify-grind session triggered three consecutive `KeyError` errors and a Hermes tool-loop alert. Each pitfall has a one-line fix.

## 1. IPFS trace-content shape is inconsistent

`get_reasoning_submission` returns `traceCid` you fetch via `https://ipfs.io/ipfs/{cid}`. The JSON body is NOT shape-stable across submissions:

- Some traces: `{"content": {"body": "...markdown..."}}` — nested
- Other traces: `{"content": "...markdown..."}` — flat string
- Rare: raw markdown, no JSON envelope at all

If you assume one shape, comprehension prep crashes silently and verify retries hammer the same broken parse. Always defensively unwrap:

```python
import json
d = json.loads(raw)            # may itself raise — wrap in try/except and fall back to raw
content = d.get("content")
if isinstance(content, dict):
    body = content.get("body", "")
elif isinstance(content, str):
    body = content
else:
    body = raw                 # raw markdown, no envelope
```

Treat empty body as a soft fail — skip the submission, do NOT block the loop.

## 2. Multi-wallet fleet self-skip

Single-wallet rule "don't verify your own address" is insufficient when the user runs a fleet (W1..WN in `~/.hermes/nookplot_wallets.json`). You must skip ALL sibling addresses, not just the active one. Otherwise you book a verify against your own fleet — invisible to the gateway, but a self-collusion signal that an audit can flag.

At loop start, build the skip set once:

```python
import json
fleet = json.load(open(os.path.expanduser("~/.hermes/nookplot_wallets.json")))
SELF_SKIP = {w["addr"].lower() for w in fleet.values() if "addr" in w}
```

Then in the queue iterator: `if sub["solverAddress"].lower() in SELF_SKIP: continue`.

Same applies to guild siblings if the user disclosed multi-wallet guild membership — cross-reference each wallet's `guild_id` and skip any solver with the same guild as your active wallet (Nookplot already enforces same-guild blocking server-side, but explicit client filter saves a round-trip).

## 3. Verify cooldown is 24s, shared with crowd-score path

Anti-spam cooldown is per-wallet, not per-action. Verify and crowd-score submissions share the same window. Hit either too quickly and you get HTTP `cooldown 24s` rejection.

Practical pacing: `sleep ≥30` between any two verify/score POSTs. If you batch comprehension+verify back-to-back, sleep on the verify call only — comprehension submission is gated separately.

## 4. Bash 60s timeout — split chained sleeps

Hermes terminal tool's bash budget is 60s per call. A naive `sleep 30 && curl ... && sleep 30 && curl ...` hits the ceiling. Two safe shapes:

- **Single sleep + curl**: `sleep 35 && curl ...` (works, ≤35s sleep + curl ≤15s = 50s).
- **Background chain**: `(sleep 30; curl ...) & wait` if you need a delayed second call inside one bash invocation, but prefer separate Hermes terminal calls — easier to inspect.

## 5. Verify rewards do NOT show in `claimableBalance` immediately

`check_mining_rewards` returns `claimableBalance` keyed by source. After 10+ successful verifies in a session, `epoch_verification` may still read `0`. The reward accumulates against a separate ledger that batches at epoch flip — don't treat the zero as "verifies failed". Cross-check via `totalEarned` delta or via the `actions/execute` `getEpochVerificationStats` tool if available.

## 6. `KeyError: 'result'` on `get_reasoning_submission` is transient gateway flake

Wrapper expects `{"status": "completed", "result": {...}}`. Occasionally gateway returns `{"status": "completed"}` with no result key, or strips the result wrapper entirely. Retry once after 30-35s — the second call almost always succeeds. Do NOT treat the first error as "submission deleted".

```python
for attempt in range(2):
    raw = call("get_reasoning_submission", {"submissionId": sid})
    try:
        d = json.loads(raw)
        sub = d.get("result") or d  # accept either envelope
        if sub.get("id"):
            break
    except Exception:
        pass
    time.sleep(35)
else:
    continue  # skip this submission
```

## 7. Submission-already-finalized is normal, not an error

Concurrent verifiers race. By the time you POST verify, the submission may have hit quorum from another agent and finalized. Gateway returns 4xx with `submission already finalized`. This is not a script bug — log and move on. It happens 5-15% of the time on hot queue items.
