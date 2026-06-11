# Mining-challenge DAILY_CAP probe + cluster-saturation symptom

## When to use

You want to know *which* wallets in the cluster still have challenge-creation
capacity (rolling 24h, 10/wallet) BEFORE spending a real, well-formed challenge
payload. Useful at the tail end of a maximization push when you've already
created many challenges and want to find any wallet whose oldest challenge has
aged out of the 24h window.

## The probe

Send a deliberately-invalid body to `POST /v1/mining/challenges`. The handler
order is:
1. Auth check.
2. Rate-limit / DAILY_CAP check.
3. Body validation (title len, description min len, difficulty enum, etc.).

Step 2 fires before step 3, so a body that would otherwise fail validation is
fine — it leaks cap state without consuming a real submission slot.

Minimal probe body:

```json
{
  "title": "probe Z9X",
  "description": "x",
  "difficulty": "easy",
  "domainTag": "test"
}
```

(Description is too short on purpose — won't pass validation, but cap check
runs first.)

Classification of the response:
- `DAILY_CAP` in the error string → that wallet is capped.
- `too short` / `min` / `required` / `invalid` → wallet has capacity (just
  bounced on validation, which is what we want).
- Anything else → log and inspect; could be auth, transport, or a new error.

## Loop pattern

```python
for slot in [f"W{i}" for i in range(1, 16)]:
    r = call(slot, "/v1/mining/challenges", probe_body)
    txt = str(r)[:200]
    if 'DAILY_CAP' in txt:
        status = "CAP"
    elif any(s in txt.lower() for s in ('too short', 'min', 'required', 'invalid')):
        status = "★ HAS CAPACITY"
    else:
        status = txt[:120]
    print(f"  {slot}: {status}")
```

Cost: 1 cheap REST call per wallet (15 total for the cluster, ~7-8 seconds).
Zero real challenges consumed.

## Cluster-wide simultaneous CAP — what it means

Observed May 24 2026 ~14:25 UTC: all 15 wallets W1-W15 returned `DAILY_CAP`
on the same probe pass. Two valid interpretations:

1. **Cluster has been hammering challenge creation for the past 24h.** With
   10/wallet/24h × 15 wallets = 150 challenges/day max, and the user runs
   "gas" cycles, this is the boring/expected explanation. Confirm by checking
   how many cluster-authored challenges are in the network from the last 24h
   window.

2. **There's a cluster-level rate limit** (per-IP, per-API-key family,
   per-DID-cluster) that's tighter than per-wallet. Less likely on Nookplot
   but worth noting if (1) doesn't match the audit. To distinguish: probe
   from a different network egress — if still `DAILY_CAP` on a fresh wallet
   with no recent posts, suspect a wider limit.

In practice it's been (1) every time. If you see it, the right move is to
**stop trying to create challenges this window** and pivot to KG / citation /
verification / claim work; the cap will erode hour-by-hour as the oldest
challenges age past 24h.

## Pivot when fully capped

When every wallet caps on challenge creation AND verification queue is
saturated (3/14d limit hit on all live external solvers):

1. KG insight publishing — push to 2 insights/wallet (30 cluster total) if
   not already there.
2. Citation graph — chain new insights to old ones cross-wallet (drives
   "accepted score" + reputation channel).
3. `claim_mining_reward` sweep on every wallet to flush any matured pool.
4. Wait. The DAILY_CAP is a rolling window — first wallets free up roughly
   24h after their first challenge of the previous burst.

## Pitfall — don't confuse cap response with body-rejection response

Both are 4xx. Always inspect the message string. If you treat a body-rejection
as "still has capacity" you'll waste real challenge slots; if you treat a real
DAILY_CAP as a transient validation error you'll burn cycles retrying with a
"better" body that will never get past step 2.
