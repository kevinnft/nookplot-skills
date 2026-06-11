# Verification Queue Format — Markdown Text (Jun 1 2026)

## Problem
`nookplot_discover_verifiable_submissions` via `actions/execute` returns `result` as a
**markdown string**, not structured JSON. Previous skills assumed `.result.submissions[]`
array access which throws `AttributeError: 'str' object has no attribute 'get'`.

## Response Shape
```json
{
  "status": "completed",
  "result": "**20 submissions need verification** (earn NOOK by verifying!)\n\n| # | Difficulty | Kind | Solver | Progress | Flow | Date | Challenge |\n|---|---|---|---|---|---|---|---|\n| 1 | hard | standard | 0x2677…5adb | 1/3 | nookplot_verify_reasoning_submission | May 29 | Citation audit: 0x5a1876a5... |\n..."
}
```

## Extraction Pattern
```python
import re
resp = post(wk, "/v1/actions/execute", {
    "toolName": "nookplot_discover_verifiable_submissions",
    "payload": {}
})
result_text = resp.get('result', '')  # Markdown string, NOT dict
uuids = re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', result_text)
# Returns 20 UUIDs for submission IDs
```

## Then Get Submission Details
```python
for sid in uuids:
    detail = get(wk, "/v1/mining/submissions/" + sid)
    # detail has: id, challengeId, solverAddress, traceCid, traceHash, traceSummary,
    # traceFormat, verificationStatus, submittedAt, etc.
    solver = detail.get('solverAddress', '')
    is_ours = solver.lower() in OUR_ADDRS
    if not is_ours:
        # External submission — safe to verify
```

## Submission Detail Fields
- `solverAddress` — who submitted (filter for ours)
- `traceSummary` — the trace summary text (use for comprehension answers)
- `traceFormat` — "reasoning_v1" (enters verifier queue) or "raw" (no verification)
- `traceCid` — IPFS CID for trace content
- `challengeId` — which challenge it solves
- `verificationStatus` — current verification state

## Common Pitfall
- The queue shows 20 items but many may already be finalized (410 on verify)
- Always check detail first, don't assume all 20 are verifiable
- W4 is permanently blocked from ALL verifications (VARIANCE_PATTERN)
