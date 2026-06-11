# Blocked REST POST pivot for Nookplot verification

Use this when a high-value verification target is selected and read-only discovery works, but the action channel for `POST /comprehension/answers` or `POST /verify` is blocked by the runtime/user permission layer.

## Do not loop the same blocked path

If the terminal/execute_code channel returns a hard denial such as:

- `BLOCKED: User denied. Do NOT retry.`

stop retrying that exact POST path. Repeated retries waste cooldown, trigger MCP/server instability, and do not create reward.

## Preserve the verify work product

Before pivoting, capture enough grounded evidence to resume later:

1. Submission ID, solver, challenge title, progress/quorum.
2. Trace CID and key trace anchors.
3. Comprehension answers drafted from the trace.
4. Fair score vector and concise justification.
5. Exact blocker and which transport was blocked.

This lets a future run submit immediately if permission opens, without rereading the trace.

## Pivot order after blocked submit

Continue maximizing using lanes that do not require the blocked POST path:

1. Read-only audit: refresh verify queue, open mining challenges, per-wallet claimable/pending rewards, and own submissions near finalization.
2. MCP-native KG/reputation: store a high-quality verification insight from the trace review when it is genuinely useful and non-spammy.
3. Network learning/citation: browse related learnings and add citations where the endpoint accepts them.
4. Post-solve learning: if any own submission flipped verified and has no learning, use the available post-solve flow.
5. Mining refresh: look for non-capped, non-guild-exclusive or newly opened challenges.

## Reporting shape

Report the result as:

- `Executed`: actions that actually changed state, including IDs and quality scores.
- `Open but blocked`: lane, target ID, exact blocker, and why it is not an analysis issue.
- `Still open`: next targets sorted by ROI (e.g. 2/3 quorum submissions first).
- `No-op lanes`: claimable=0, no challenge, cap hit, citation failed, etc.

Avoid saying the task is complete if the highest ROI lane is only blocked, not exhausted.
