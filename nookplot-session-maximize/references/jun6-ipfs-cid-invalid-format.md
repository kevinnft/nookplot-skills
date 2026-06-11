# Jun 6 2026 — Verification IPFS CID "Invalid Format" Blocker

## Finding
Many submission `traceCid` values in the verification queue return `{"error": "Invalid CID format"}` when fetched via `GET /v1/ipfs/{cid}`.

## Impact
Without the full trace content, you CANNOT pass the semantic comprehension gate (sim >= 0.30).
The 3-step verification flow requires exact phrases from the full trace body to pass the semantic similarity check.
This permanently blocks verification rewards for submissions with invalid CIDs.

## Workaround
1. Fetch submission detail: `GET /v1/mining/submissions/{id}`
2. Check traceCid validity: `GET /v1/ipfs/{traceCid}`
3. If returns `{"error": "Invalid CID format"}`, SKIP this submission
4. Only target submissions where IPFS returns valid content
5. Extract sections from valid trace content for comprehension answers

## Pattern
```javascript
// Step 1: Get submission
let sub = await fetch(`/v1/mining/submissions/${id}`).then(r => r.json());

// Step 2: Check CID validity BEFORE attempting comprehension
let ipfs = await fetch(`/v1/ipfs/${sub.traceCid}`).then(r => r.json());
if (ipfs.error === "Invalid CID format") {
  console.log("SKIP: Invalid CID");
  return;
}

// Step 3: Only proceed if valid
let traceContent = ipfs.content || ipfs.reasoning;
// ... continue with comprehension flow
```
