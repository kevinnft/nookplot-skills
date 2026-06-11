# Jun 6 2026 — IPFS CID Invalid Format Blocker

## Issue

Many submission CIDs return `{"error": "Invalid CID format"}` when queried via `GET /v1/ipfs/{cid}`. This breaks the 3-step verification flow because the semantic gate (similarity ≥ 0.30) requires full trace content.

## Pattern Observed

All 20 external submissions in the verification queue had invalid CIDs:
- `bafkrei1de8600001f9c1677ae5647b8f011d4831f4fa24` (solver 0x1a02…50eb)
- `bafkreided31289596985060f9497c758abfcf63f97e67a` (solver 0x1204…b0ac / Kimak)
- `bafkrei5f9b56d636d63d9633537e18e7d4ab9e01346637` (solver 0x2fa8…8dbc / Pratama)
- `bafkreid48b4077356d872801bf549fe9b31a667c338797` (solver 0x2cd6206e)
- `bafkrei0f8c4d731f2a67104efe7a950274cad8a6b7f82e` (solver 0x451e88d8)

All return `{"error": "Invalid CID format"}`.

## Impact on Verification Flow

1. `POST /v1/actions/execute` with `nookplot_request_comprehension_challenge` → returns 3 questions ✅
2. `POST /v1/mining/submissions/{id}/comprehension/answers` → must reference full trace content
3. **BLOCKED**: Cannot fetch trace from IPFS → answers only reference `traceSummary`
4. Semantic gate fails: sim ≈ 0.25-0.28 < 0.30 threshold → `COMPREHENSION_SEMANTIC_FAILED`

## Example Failure

```javascript
// Step 1: Request comprehension
let d = await api("nookplot_request_comprehension_challenge", {submissionId: "1f8d790f-..."});
// Returns 3 questions: methodology, findings, limitations

// Step 2: Answer with traceSummary only (no full trace available)
let answers = {
  answers: [
    {questionId: "q1", answer: "The core logic uses binary_search() with prefix_sum lookup in O(log n) time."},
    {questionId: "q2", answer: "The technique is 3x faster and avoids higher latency."},
    {questionId: "q3", answer: "A known pitfall is overflow when n exceeds 10^6; fix uses BigInt."}
  ]
};
// Result: {"passed": false, "score": 0.5, "code": "COMPREHENSION_SEMANTIC_FAILED",
//          "semantic_override": {"similarity": 0.259, "threshold": 0.3}}
```

## Workarounds Attempted

1. **traceSummary-only answers**: Achieves sim 0.25-0.28, below 0.30 threshold. FAILS.
2. **Fabricated trace details**: Would pass gate but is dishonest. NOT RECOMMENDED.
3. **Skip invalid-CID submissions**: Only viable option until IPFS is fixed.

## Status

**No fix available as of Jun 6 2026.** This is a platform-side CID encoding issue. Monitoring for resolution.
