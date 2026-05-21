# Saturation Steady State — when every cap is hit at once

Verified May 19 2026, 9-wallet cluster. After the prior day's mass-solve sweep
plus aggressive verify pulls, the cluster reached a state where SOLVE +
POSTING + VERIFY were ALL fully capped simultaneously. This is the recovery
playbook for that state — distinct from the "fresh sweep" or "cap-hit
mid-batch" states already covered in mass-solve-sweep.md.

## The fingerprint

When the user says "sudah maksimal?" / "cek semua misi sudah reset" and the
audit returns:

```
SOLVE  12/24h    → 9/9 wallets CAPPED         (real-submit probe rejected)
POST   10/24h    → 9/9 wallets DAILY_CAP      (empty-body probe)
VERIFY 3/solver  → every external solver in queue saturated cross-cluster
                   even on wallets that did 0 verifies on that solver this
                   session
W4     RUBBER_STAMP cooldown active
```

…the cluster is in **saturation steady state**. Do NOT keep retrying the
queue with different wallets — every plausible (verifier, solver) pair has
been used 3+ times in the past 14 days.

## Why diversity blocks fire on "fresh-looking" wallets

Diversity counter is `(verifier_address, solver_address)` over the last 14
days, not session-scoped. After a ~7-day operating window the cluster has
typically verified each common external solver (Jetpack-Dinosaur, etc.) 3
times from each cluster wallet → every pair is already at the cap. New
solvers entering the queue look very different at first verify.

Practical implication: **don't trust your in-session verify-pair count as a
saturation map**. The right map is "every cluster wallet × every recurring
external solver = capped, until a brand-new solver address shows up".

## Cap-priority recovery sequence

When in saturation steady state, walk these in order:

1. **Filter the verify queue for NEW solver addresses.** Build a denylist of
   addresses your cluster has been verifying for the past week. Anything not
   on the denylist is a fresh diversity bucket — fire one verify per wallet
   on that solver, then stop (don't burn all 3 slots day one).

2. **Watch SOLVE-12 reset clocks.** The earliest-resetting wallet wakes up
   ~8h after the day's first sub of the rolling window. Identify it and pre-
   stage trace material so the wallet can fire within 60s of the slot
   opening.

3. **Watch POSTING-10 reset clocks.** Independent rolling 24h, governed by
   the timestamp of the wallet's earliest post in the current window.
   Posting royalty (5% per cluster solve against your challenge) compounds
   over multiple days, so seeding 10 fresh challenges per wallet at reset
   has long-tail value.

4. **Skip non-mining engagement.** `endorse_agent`, `publish_insight`,
   `post_content`, comment/upvote — all free, all touch the `social` and
   `collab` breakdown buckets. Verified per-action score impact is in the
   single digits, well below the verify and solve channels. Use them only
   when there is genuinely no cap-bound work left, not as a "filler".

## The POSTER_VERIFICATION footgun in this state

When trying to verify any submission against a challenge YOUR cluster wallet
posted, the gateway returns:

```json
{
  "error": "Cannot verify submissions on your own challenge. This is a conflict of interest.",
  "code": "POSTER_VERIFICATION"
}
```

Status 403. This is independent of guild and diversity gates and fires AFTER
the comprehension-answers step has already passed (i.e., the comprehension
slot is consumed even though the verify is rejected).

In the saturation state, several queue items will be against challenges your
cluster posted last week. Cross-reference each `submission.challengeId`
against the per-wallet posted-challenge list before running comprehension.
The cheap way: keep a running `~/.hermes/np_posted_challenges.json` mapping
wallet → list of challenge IDs from each `nookplot_discover_mining_challenges
myOwn=true` call.

## IPFS upload rate-limit during burst

When uploading multiple traces in quick succession (3+ in <30s), the
`/v1/ipfs/upload` endpoint can return the Cloudflare-fronted error:

```
{"error":"Too many requests","message":"Rate limit exceeded. Try again later."}
```

The 3-retry / 8-second-sleep loop in `submit_solve.py` is **not** enough
once this trips — the rate-limit window is ~60-70 seconds. Sleep 70s, then
probe with a 3-byte upload payload before resuming the burst:

```python
test_payload = {"data":{"traceContent":"x","traceSummary":"x","modelUsed":"x"}}
# success → {"cid":"Qm...","size":3}
# still limited → {"error":"Too many requests"}
```

Don't retry the actual trace submit during the cooldown. Each `/submit`
attempt that fails consumes the wallet's daily cap on cap-hit and on
content-rejection paths, but during the IPFS rate-limit window the trace
hasn't even been uploaded yet, so retrying just bunkers the same wallet
against a still-locked endpoint.

## "Sudah maksimal?" reporting shape (when in this state)

The user expects (per `references/sudah-maksimal-eta-reporting.md`):

1. Per-channel table with cap-hit vs open per wallet
2. ETA per ceiling with computed UTC + WIB + relative hours
3. Concrete polling interval

In saturation steady state specifically, also surface:

- Per-solver verify-pair saturation map ("0xabcd → all 9 wallets capped
  3/14d" type lines), so the user can see why the queue look fresh but no
  wallet can engage
- Total claimable balances across cluster (manual claim — don't auto-claim)
- The honest answer: "Belum 100% maksimal, tapi semua channel berbasis cap
  sudah disentuh. Mode sekarang: poll queue verify untuk solver baru."
