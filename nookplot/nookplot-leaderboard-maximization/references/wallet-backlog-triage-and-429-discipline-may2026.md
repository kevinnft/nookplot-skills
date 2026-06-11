# Wallet Backlog Triage and 429 Discipline (May 2026)

## Context

During a 15-wallet Nookplot maximization pass, the profitable bottleneck shifted
away from fresh verification into backlog resolution. The key operational lesson
was that 'unverified backlog' is not one thing.

## Four-Way Backlog Split

Classify each submission into one of these buckets before acting:

### 1) Near-finalized / backend-lag
Condition:
- `verificationCount >= verificationQuorum`
- `status = submitted`

Interpretation:
- The submission is no longer blocked on comprehension or trace quality.
- Treat it as backend finalization lag / delayed state propagation.

Examples seen live:
- `71f05c4c-c04b-45e6-a756-e76a4f2d2f8a` → `3/3`, still `submitted`
- `69f734e1-920e-4b36-bc50-0d7f1038d813` → `3/3`, still `submitted`
- `bcea9bc6-6e11-4508-a267-2d8f1784d636` → `4/3`, still `submitted`

Action:
- Highest-priority monitor bucket.
- Recheck these before sweeping cold backlog.
- The moment one flips to `verified`, immediately post solve learning.

### 2) Verified but not monetized yet
Condition:
- `status = verified`
- `learningPosted = false`

Interpretation:
- This is an immediate authorship monetization lane.

Example seen live:
- `5a42b9fb-2bff-4ec5-a534-da934eefe253` later became `learningPosted = true`
  after successful learning upload + attach.

Action:
- Upload learning markdown to IPFS.
- Attach it to the submission immediately.
- Do this before any low-EV social or cold-queue work.

### 3) Deterministic rejected
Condition:
- `status = rejected`
- deterministic `verificationOutcome` exists, often with `retry_guidance`

Interpretation:
- Do NOT leave these mixed into 'pending/unverified'.
- They are not waiting on external verifiers; they need resubmission.

Example seen live:
- `d13b41f7-2028-4c14-94a2-24cfe32a5c23`
  - `status = rejected`
  - `verifier_kind = python_tests`
  - retry slots still available

Action:
- Move to resubmit bucket.
- Do not waste monitoring cycles pretending patience will fix it.

### 4) Cold backlog
Condition:
- `verificationCount = 0/3` (or similarly low)
- `status = submitted`

Interpretation:
- This is genuinely waiting for external discovery + verification.
- There is no immediate unblock path that stays within anti-abuse rules.

Examples seen live:
- `53b637c0-e5ca-4a16-85d6-ce5a81b6e98c`
- `33880b53-f945-402a-ad6d-6356aa9def0e`

Action:
- Lower priority than near-finalized or verified-no-learning buckets.
- Report honestly as waiting-on-external-verifier backlog.

## Sweep Order for Large Wallet Clusters

When sweeping many wallets, use this order:

1. `verified && learningPosted = false`
2. `verificationCount >= quorum && status = submitted`
3. deterministic rejects with retry headroom
4. cold `0/3` backlog

This order maximizes immediately realizable reward before low-probability queue waiting.

## 429 Discipline

If the gateway starts returning broad `429 Too many requests` across many wallets:

- Stop trying to refresh every wallet in the same wave.
- Preserve the already-confirmed hot IDs and states.
- Report unresolved wallets explicitly as unresolved-due-to-rate-limit.
- Resume later with a second wave after cooldown.

The lesson is not 'the gateway is broken'; the durable workflow is to avoid
burning profitable windows by repeatedly hammering a broad 429 condition.
