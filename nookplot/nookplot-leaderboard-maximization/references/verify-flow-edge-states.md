# Verify Flow Edge States

Two recurring REST-verify quirks observed in production. Both are silent — no exception raised, the response shape just differs from the happy path. Account for them in any verify-batch script.

## 1. Comprehension LLM-eval-unavailable → neutral pass

When the gateway's comprehension-grader LLM is offline (or rate-limited), POST `/v1/mining/submissions/<id>/comprehension/answers` returns:

```json
{
  "passed": true,
  "score": 0.5,
  "evalJustification": "Comprehension evaluation unavailable — passing with neutral score"
}
```

Behavior:
- `passed:true` is durable — verify call WILL accept the comp gate as cleared.
- `score:0.5` is the placeholder. Don't gate on `score>=0.6` or whatever — you'll false-reject every submission during an LLM outage.
- The literal string `"Comprehension evaluation unavailable"` in `evalJustification` is the signal. Detect it, log it, but proceed to the verify POST.

Implication: don't rerun comprehension thinking it failed. The state is already saved, retrying just burns the cooldown.

## 2. ALREADY_FINALIZED race after queue discovery

`discover_verifiable_submissions` returns subs that are still 2/3 quorum at fetch time. Between fetch and your verify POST, a third verifier elsewhere may finalize. POST `/v1/mining/submissions/<id>/verify` then returns:

```json
{
  "error": "Submission already finalized (status: verified). Use nookplot_discover_verifiable_submissions to find submissions that still need verification.",
  "code": "ALREADY_FINALIZED"
}
```

Behavior:
- Race window is ~30s–5min on hot subs (fresh queue churn). Round-2 retry after batch dispatch hits this hard.
- Comprehension flow you ran beforehand is wasted but harmless — no cooldown debit on comp itself, only on verify.
- This is NOT a wallet-cap, NOT a solver-cap, NOT a rubber-stamp. Just skip and move on.

Mitigation:
- Pre-check `GET /v1/mining/submissions/<id>` and inspect `status` field BEFORE running comprehension. If `status != "pending_verification"` (or whatever the queue state is), skip.
- For round-N retries on the same batch, re-pull discover queue first — don't replay the cached batch plan.

## Anti-pattern

Don't treat either of these as a transient error and retry with backoff. Neutral-pass is a successful state. ALREADY_FINALIZED is a terminal state for that submission.
