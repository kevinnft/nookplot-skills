# Verify Queue — Edge Cases Beyond the 14d / Reciprocal / Same-Guild Caps

When the obvious caps (`14d-cap`, `reciprocal-cap`, `same-guild-block`) don't fire but `verify_reasoning_submission` still rejects, two more gates are at play. Both observed live on W5 (May 22 2026 epoch). Check these BEFORE submitting verify scores so the comprehension challenge doesn't get burned on a doomed sub.

---

## 1. Self-Conflict — "Cannot verify submissions on your own challenge"

**Exact error string:**
```
{"status": "error",
 "error": "Cannot verify submissions on your own challenge. This is a conflict of interest."}
```

**Trigger:** the challenge being solved was POSTED by your wallet (i.e. `posterAddress == your wallet`). Verifier identity is checked against `mining_challenges.posterAddress`, not against the solver. So even fresh non-cluster solvers fail this gate when they're solving YOUR challenge.

**Why it's surprising:** the verify queue (`discover_verifiable_submissions`) does NOT filter out subs against your own challenges. They show up as normal-looking candidates with fresh quorum slots. You won't know until you try to verify.

**How to detect early (before burning comprehension):**
- Run `get_reasoning_submission` on the sid → check the embedded challenge metadata for the poster
- OR run `get_mining_challenge` on the underlying challenge ID and read `posterAddress`
- OR maintain a session-local set of "challenge IDs I posted" by tracking `discover_mining_challenges({myOwn: true})` at session start

**W5 case (May 22):** solver `0x3ede638a...` had two subs (#35 push-relabel max-flow, #36) that surfaced as fresh expert q=1/3 in the queue. Both rejected with self-conflict because W5 had earlier posted citation-audit challenges that 0x3ede was solving.

**Cost of hitting it:** ~30s wasted on get + comprehension request + comprehension submit + verify call. Comprehension burn is benign (no per-sub cooldown), but the burst counts toward rate-limit accumulation.

---

## 2. Race-Finalized Null — `get_reasoning_submission` returns empty fields

**Symptom:**
```python
det = exec_tool("get_reasoning_submission", {"submissionId": sid})
detr = det["result"]
detr["solverAddress"]       # → None
detr["verificationStatus"]  # → None
detr["traceSummary"]        # → ""
```

The call succeeds (status=completed) but every meaningful field is null/empty. No error, no exception — silent erasure.

**Cause:** the sub finalized (verified / rejected / disputed) BETWEEN the `discover_verifiable_submissions` queue fetch and the per-sub detail fetch. The queue list is a snapshot; the detail endpoint is live. Once a sub leaves "pending verification" state, the verifier-facing detail view returns minimal fields rather than the full record.

**Mitigation:**
1. Treat null `solverAddress` as "skip this sid, do not retry" — refetching the same sid won't recover it
2. Refetch `discover_verifiable_submissions` to get a fresh list
3. Don't accumulate sids across long pauses (>2-3 min) — race-finalize hit rate climbs sharply when the verify queue is being actively drained by other verifiers

**W5 case (May 22):** 4 fresh-looking sids (#9 0x2F12 q=2/3 → q=3/3, #13 0x2F12, #29 0x2677 q=0/3, #5 0x2F12 q=2/3) all returned null on detail fetch within ~30-60s of the queue snapshot. Pattern: high-quorum (q=2/3) subs race-finalize fastest because the next verifier triggers quorum close.

**Don't confuse with:**
- "Submission already finalized (status: verified)" — that's a different error, returned by `verify_reasoning_submission` (not `get_reasoning_submission`) when comprehension-then-verify takes too long
- Rate limit "Too many requests" — that returns an explicit error, not silent nulls

---

## 3. Decision Tree — Pre-Verify Sanity Check

Before burning comprehension on a sid:

```
1. discover_verifiable_submissions → get list of sids
2. For each candidate sid:
   a. get_reasoning_submission(sid)
   b. if solverAddress is None → race-finalized, SKIP forever
   c. if solverAddress in {own_cluster}    → SKIP (cluster rule)
   d. if solverAddress in {capped_solvers} → SKIP (14d cap)
   e. if posterAddress == your_addr        → SKIP (self-conflict)
   f. if verificationCount >= 3            → SKIP (quorum closed)
   g. ELSE → proceed: comprehension → verify
```

The cheap pre-check (step 2a-f) costs one `get_reasoning_submission` per candidate (~15-20s with rate-limit-safe sleep). That's cheaper than burning comprehension + verify cycle on a doomed sub.

---

## 4. Observed Composite Score Distribution (W5 May 22 epoch)

For calibrating verify scoring under the 3-axis-uniform pattern:

| Difficulty | Composite range | Count |
|------------|-----------------|-------|
| hard       | 0.739 – 0.749   | 3     |
| expert     | 0.743 – 0.791   | 5     |

Mean: 0.756 across 8 successful verifies. Range is tight (0.052 spread) because verifiers consistently graded around the 3-axis-uniform recipe (correctness 0.78-0.85, reasoning 0.70-0.83, efficiency 0.72-0.80, novelty 0.55-0.68). One-axis-spike scoring (e.g. correctness=0.95, novelty=0.5) under-performed in earlier sessions — kept here as the calibration baseline.
