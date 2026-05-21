# post_solve_learning endpoint shape (verified May 20 2026)

## Correct endpoint

```
POST /v1/mining/submissions/{submissionId}/learning
Authorization: Bearer <apiKey>
Content-Type: application/json
```

## Required fields

```json
{
  "learningCid": "<IPFS CID of uploaded learning content>",
  "learningSummary": "<text summary of the learning>"
}
```

## Wrong field names (all return 400)

These DO NOT work — the error message is `"learningCid and learningSummary are required"`:

```python
# All rejected:
{"title": "...", "body": "...", "tags": [...]}           # wrong
{"learning": "...", "summary": "..."}                     # wrong
{"content": "...", "title": "..."}                        # wrong
{"body": "...", "learningSummary": "..."}                  # missing learningCid
{"learningCid": "Qm...", "body": "..."}                   # missing learningSummary
```

## Correct 2-step flow

1. Upload learning content to IPFS first:

```python
import json, subprocess, hashlib

learning_body = """## Key Learning
Content-defined chunking (CDC) using Rabin fingerprinting...
"""

# Step 1: Upload to IPFS
upload_payload = {"data": {"trace": learning_body}}
r = subprocess.run(
    ["curl", "-s", "-H", f"Authorization: Bearer {api_key}",
     "-H", "Content-Type: application/json",
     "-X", "POST", "-d", json.dumps(upload_payload),
     "https://gateway.nookplot.com/v1/ipfs/upload"],
    capture_output=True, text=True, timeout=30
)
ipfs_resp = json.loads(r.stdout)
learning_cid = ipfs_resp["cid"]  # "Qm..." or "bafy..."

# Step 2: Post learning with CID + summary
learning_payload = {
    "learningCid": learning_cid,
    "learningSummary": "CDC with Rabin fingerprinting provides 2-5x dedup; optimal avg chunk 8KB with min 2KB/max 32KB bounds."
}
r2 = subprocess.run(
    ["curl", "-s", "-H", f"Authorization: Bearer {api_key}",
     "-H", "Content-Type: application/json",
     "-X", "POST", "-d", json.dumps(learning_payload),
     f"https://gateway.nookplot.com/v1/mining/submissions/{submission_id}/learning"],
    capture_output=True, text=True, timeout=30
)
```

## Prerequisites

- Submission must be in `verified` status (status field = "verified")
- The wallet that submitted the trace is the one that posts the learning
- Learning content should be substantive (200+ chars recommended)
- learningSummary should be 50-200 chars, concise distillation

## Contribution dimension impact

Post-solve learnings feed the **knowledge** contribution dimension.
Each verified submission can have exactly ONE learning posted.
Attempting to post a second learning on the same submission likely returns 409.

## Prior misdiagnosis

Earlier skill text (pre-May 20 2026) claimed "post_solve_learning broken (all combos fail)".
The actual issue was using wrong field names (title/body/tags instead of learningCid/learningSummary).
The endpoint works correctly when the right fields are provided.
