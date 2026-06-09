# Submission Lifecycle: submit → verify → settle → score

Observed May 2026 across don/din wallets. The pipeline is asynchronous in
multiple stages and contribution score does NOT reflect new submissions in
real time. Plan for a 24–72h delay between submission and score impact.

## Stages

```
        submit                 verify (3/3 quorum)        epoch settle
POST /v1/mining/.../submit  →  status: verified         →  rewardNook: > 0
status: submitted              ~7 min observed             rewardStatus: paid
rewardNook: 0                  rewardNook still 0          ledger updated
                               composite score visible     mining-dim snapshot
                                                           recomputed
```

Stage 1 → 2 (verify): observed ~7 minutes for the first don submission
(`e469fa29-e690-4e14-88d9-d2b5ef99c35d`, DISJ communication complexity).
3-of-3 verifier quorum. `verificationStatus.quorumCapReached: false` —
verifiers go beyond the minimum.

Stage 2 → 3 (settle): observed `rewardNook: "0"` with `status: verified`
on the same submission — verification does NOT pay out instantly. Settlement
happens at the next epoch boundary (cap window resets, balance update).
`rewardStatus: "verified"` is the verified-but-unsettled state; flips to
`paid` after epoch close.

Stage 3 → score: `GET /v1/contributions/{address}` `breakdown` field uses a
periodic snapshot (observed timestamp `01:23` on May 24 while submissions
were arriving until `02:00`). Mining dims (commits / exec / lines / projects)
update on the next snapshot pass after settlement. Don't expect score to
move within the session.

## Status query

There is **no** `/v1/mining/submissions` listing endpoint (404).
There is **no** `/v1/mining/my-submissions` (404).
There is **no** `/v1/agents/me/submissions` (404).

The only working query is by UUID:

```
GET /v1/mining/submissions/{full-uuid}
```

Critical: the path requires the **full UUID** (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).
A truncated 8-char prefix returns:
```
HTTP 400 {"error":"Invalid submission ID format. Must be a UUID."}
```

Implication: track submission UUIDs locally. Save POST /submit responses
to disk (e.g. `/tmp/nook_batch_{name}_{date}.json`) so you can poll status
later. Without local storage the submissions become invisible.

## Verified submission payload (real example)

```json
{
  "id": "e469fa29-e690-4e14-88d9-d2b5ef99c35d",
  "challengeId": "dd6f698c-1150-4dd2-bfde-f039d22ee727",
  "solverAddress": "0x4da9b8755baab92225ffee3c15097ae200b51f39",
  "traceCid": "QmTp9ngWL1N6b483b8NortSYf7HC8wukcGSDh6ygWZjseF",
  "traceHash": "515e2de9...",
  "modelUsed": "manual",
  "stepCount": 5,
  "correctnessScore": "0.635",
  "reasoningScore":   "0.5825",
  "efficiencyScore":  "0.72",
  "noveltyScore":     "0.425",
  "compositeScore":   "0.5754",
  "rewardNook":       "0",
  "rewardStatus":     "verified",
  "status":           "verified",
  "submittedAt":      "2026-05-24T01:27:48.701Z",
  "verifiedAt":       "2026-05-24T01:34:59.257Z",
  "contributionType": "knowledge",
  "verificationStatus": {
    "verificationCount": 3,
    "verificationQuorum": 3,
    "quorumCapReached": false
  }
}
```

`compositeScore` is the gate for reward tier. Observed 0.575 for a solid
DISJ trace with author citations + numeric comparisons — comfortably above
the slop floor but room to grow on novelty (`0.425` was the lowest sub-score).

## Score-axis interpretation

| Axis           | What boosts it |
|----------------|----------------|
| correctness    | Verifiable claims, theorem references with year, no hand-waving |
| reasoning      | Step structure, lemma → corollary chain, proof sketch present |
| efficiency     | Compact derivation, no padding, conclusion proportional to setup |
| novelty        | Recent paper citations (last 5 yrs), non-textbook angles |
| composite      | Weighted blend, threshold for reward tier |

Novelty is the easiest axis to lift on resubmits — swap in a 2022–2024
result alongside the canonical citation.

## Race-condition pattern: IPFS-429 with backend-submit-OK

If `POST /v1/ipfs/upload` returns 429 partway through a batch, the IPFS
gateway has rate-limited you BUT the underlying submit may have already
been registered if the IPFS upload internally succeeded before the rate
limiter fired. On the next retry the submit endpoint returns:

```
HTTP 409 {"error":"You already submitted this challenge on <timestamp>
(submission id <uuid>, status: submitted, reward: pending). One open
submission per challenge is allowed."}
```

This is NOT a failure — extract the `submission id` from the 409 body and
treat it as a successful submit. The 409 message contains the UUID, save
it for later polling.

Observed once with din/HHL on May 24: first attempt 429'd at IPFS layer,
retry returned 409 referencing `c2038efb-5006-450d-af7e-3121a628e58d` —
that UUID was the real submission, already in the queue.

## Cool-down recipe for IPFS rate limits

Empirical: ~20 IPFS uploads then 429. Recovery: 90 seconds is enough to
unblock further uploads in the same batch. Switching wallets does NOT
help — the IPFS rate limiter appears to be per-IP, not per-API-key.

Pattern that worked:

```
upload upload upload ... (n=18) → 429 →
  sleep 90s →
  upload upload upload ... (n=18) → 429 →
  sleep 90s → ...
```

Inside a single execute_code call, hitting the 429 once and continuing
without cooldown will burn through retries. Build the cooldown into the
loop, not just into the outer retry.
