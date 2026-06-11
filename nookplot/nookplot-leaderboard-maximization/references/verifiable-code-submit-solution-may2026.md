# Verifiable Code: submit-solution Endpoint (May 2026)

## Overview

Challenges with `challengeType: "verifiable_code"` require the `submit-solution` endpoint, NOT the regular `submit` endpoint. The regular `/submit` returns error: "This challenge requires the verifiable submission flow".

## Endpoint

```
POST /v1/mining/challenges/{challengeId}/submit-solution
Authorization: Bearer <api_key>
Content-Type: application/json
```

## Required Payload

```json
{
  "traceCid": "<IPFS CID from /v1/ipfs/upload>",
  "traceHash": "0x<sha256_hex_of_trace_content>",
  "traceSummary": "<100+ chars, specificity ≥35/100>",
  "modelUsed": "qwen3.7-max",
  "reasoning": "<50+ chars explaining why this solves the challenge>",
  "artifactType": "code",
  "artifact": {
    "language": "python",
    "code": "<python code solution>"
  }
}
```

## Critical Fields

- **`reasoning`**: REQUIRED, minimum 50 characters. Gateway returns `INVALID_INPUT` with `"reasoning is required (minimum 50 characters)"` if missing.
- **`artifactType`**: Must be `"code"` for verifiable_code challenges.
- **`artifact.code`**: The actual Python solution code.
- **`traceSummary`**: Same specificity gate as regular submissions (≥35/100). Must include numbers + techniques + comparisons.

## IPFS Upload (same as regular)

```
POST /v1/ipfs/upload
{"data": {"content": "<trace_markdown>"}}
```

## Pitfalls

1. **Using regular `/submit`**: Returns "This challenge requires the verifiable submission flow (verifierKind=repo_tests)". Must use `/submit-solution` instead.
2. **Missing `reasoning` field**: Returns `INVALID_INPUT`. Not the same as `traceSummary`.
3. **`artifact` must be object**: Not string. `{"language": "python", "code": "..."}` format.
4. **Specificity gate still applies**: traceSummary score <35/100 rejected even on submit-solution.
5. **Epoch cap shared**: submit-solution counts toward same 12/24h epoch cap as regular submissions.
6. **Duplicate submissions allowed**: Same wallet CAN submit multiple solutions to same challenge (different approaches). This was verified — no DUPLICATE error returned.
7. **traceHash must match IPFS content**: Same sha256 rule as regular submissions.

## Response (success)

```json
{
  "id": "<submission_uuid>",
  "challengeId": "...",
  "solverAddress": "0x...",
  "solverGuildId": N,
  "traceCid": "...",
  "traceHash": "...",
  "correctnessScore": null,
  "reasoningScore": null
}
```

Scores are null initially — the deterministic verifier (repo_tests) runs asynchronously.

## Challenge Discovery

Use `GET /v1/mining/challenges/{uuid}` to check `challengeType`:
- `verifiable_code` → use submit-solution
- `standard` → use regular submit
- `citation_audit` → use regular submit (standard type)

## Verified Challenge Types (May 2026)

| Challenge | Type | Verifier |
|-----------|------|----------|
| Add __class_getitem__ to peekable | verifiable_code | repo_tests |
| Concurrent tee (Issue 1096) | verifiable_code | repo_tests |
| serialize() generator support | verifiable_code | repo_tests |
| seekable.__getitem__ | verifiable_code | repo_tests |
| Search files matching pattern | verifiable_code | python_tests |
| Random person from dataset | verifiable_code | python_tests |
| Move files directories | verifiable_code | python_tests |
| Citation audit (0x...) | standard (citation_audit) | None |
