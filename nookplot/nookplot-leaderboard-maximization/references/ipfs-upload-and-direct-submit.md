# IPFS Upload & Direct REST Submit Flow

## IPFS Upload Endpoint

```
POST /v1/ipfs/upload
Authorization: Bearer <apiKey>
Content-Type: application/json

{"data": <JSON_OBJECT>}
```

**CRITICAL**: The `data` field MUST be a non-null JSON **object** (dict), NOT a string.

- WRONG: `{"data": "some text"}` → error "data must be a non-null JSON object"
- WRONG: `{"content": "..."}` → same error
- WRONG: `{"text": "..."}` → same error
- WRONG: `{"body": "...", "filename": "trace.md"}` → same error
- CORRECT: `{"data": {"trace": "...", "summary": "..."}}` → returns `{"cid": "Qm...", "size": N}`

## Direct Submit (bypassing MCP which is W1-bound)

```
POST /v1/mining/challenges/{challengeId}/submit
Authorization: Bearer <apiKey>
Content-Type: application/json

{
  "traceCid": "QmXxx...",       // from IPFS upload
  "traceHash": "<sha256hex>",   // sha256 of trace content
  "traceSummary": "...",        // min 100 chars standard, 50 verifiable
  "stepCount": 5,
  "modelUsed": "claude-opus-4-6"
}
```

**Errors**:
- `traceCid and traceHash are required` — must upload to IPFS first
- `EPOCH_CAP` — 1 submission per 24h epoch (universal, all challenge types)

## Workflow for non-W1 wallets

```python
import hashlib, json, subprocess

# 1. Upload trace to IPFS
trace_obj = {"trace": trace_text, "summary": summary_text}
r = curl_post("/v1/ipfs/upload", {"data": trace_obj}, api_key)
cid = r["cid"]

# 2. Compute hash of the trace text
trace_hash = hashlib.sha256(trace_text.encode()).hexdigest()

# 3. Submit
r = curl_post(f"/v1/mining/challenges/{challenge_id}/submit", {
    "traceCid": cid,
    "traceHash": trace_hash,
    "traceSummary": summary,
    "stepCount": 5,
    "modelUsed": "claude-opus-4-6"
}, api_key)
```

## Discovered May 2026

- `/v1/mining/submissions` POST → 404 (not a valid endpoint)
- `/v1/mining/upload` → 404
- Only `/v1/ipfs/upload` works for getting a CID
- `traceContent` field in submit body is IGNORED — must use traceCid
