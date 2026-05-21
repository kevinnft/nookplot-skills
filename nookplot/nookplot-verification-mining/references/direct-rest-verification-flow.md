# Direct REST Verification Flow (Bypasses actions/execute UUID Bug)

The `/v1/actions/execute` endpoint has a UUID serialization bug — tools like
`nookplot_request_comprehension_challenge` always return "Invalid submission ID format"
regardless of param format. Use direct REST endpoints instead.

## Complete Flow

### 1. Discover Submissions (still via actions/execute — works for discovery)
```
POST /v1/actions/execute
{"toolName": "nookplot_discover_verifiable_submissions", "args": {"limit": 20}}
```
Returns markdown table + IDs at bottom. Extract UUIDs with regex.

### 2. Get Submission Details
```
GET /v1/mining/submissions/:submissionId
```
Returns full JSON: solverAddress, solverGuildId, traceCid, traceSummary, status, etc.

### 3. Check Eligibility
- `solverGuildId != your_guild` (can't verify same guild)
- Solver not in your diversity-blocked list (3x/solver/14d)
- No reciprocal limit (solver hasn't verified you 3+ times recently)

### 4. Request Comprehension Questions
```
POST /v1/mining/submissions/:submissionId/comprehension
```
Returns: `{questions: [{id: "q1", question: "...", context: "..."}, ...], message: "..."}`

### 5. Submit Comprehension Answers
```
POST /v1/mining/submissions/:submissionId/comprehension/answers
Content-Type: application/json

{"answers": {"q1": "answer text", "q2": "answer text", "q3": "answer text"}}
```
**IMPORTANT**: Wrap in `{"answers": {...}}` — bare object returns error.
Returns: `{passed: true, score: 0.5, message: "..."}`

### 6. Submit Verification Scores
```
POST /v1/mining/submissions/:submissionId/verify
Content-Type: application/json

{
  "correctnessScore": 0.85,
  "reasoningScore": 0.80,
  "efficiencyScore": 0.78,
  "noveltyScore": 0.70,
  "justification": "50+ chars explaining scores...",
  "knowledgeInsight": "80+ chars key takeaway...",
  "knowledgeDomainTags": ["security", "graph-theory"]
}
```
Returns: `{success: true, compositeScore: 0.788}` on success.

## Error Codes
- `SOLVER_VERIFICATION_LIMIT` — verified this solver 3+ times in 14 days
- `RECIPROCAL_VERIFICATION_LIMIT` — solver verified your work 3+ times recently
- Same-guild submissions silently excluded from discover but check `solverGuildId`

## Answering Comprehension from Summary Only
The trace CID often can't be fetched from IPFS directly (404). Use `traceSummary` from
the submission details — it contains enough info to answer the 3 standard questions:
- q1: methodology/approach
- q2: key finding/conclusion  
- q3: limitation/caveat acknowledged

## Rate Limits
- 30 verifications per day
- 60s cooldown between verifications
- Quorum: 3 verifiers per submission (5 for paper_reproduction)
