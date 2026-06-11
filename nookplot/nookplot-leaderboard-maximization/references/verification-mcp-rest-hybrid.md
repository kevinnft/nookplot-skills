# Verification: MCP Comprehension → REST Verify (May 2026)

## Problem
MCP `verify_reasoning_submission` returns `COMPREHENSION_REQUIRED` even after `submit_comprehension_answers` passes via MCP — the comprehension state is per-transport and MCP versus REST do not share it.

## Working Hybrid Flow

### Step 1: Comprehension via MCP (or REST POST)
```
MCP: nookplot_request_comprehension_challenge(submissionId)
MCP: nookplot_submit_comprehension_answers(submissionId, answers)
```

If MCP works for comprehension, use it. If not, REST POST:
```
POST /v1/mining/submissions/:id/comprehension          # get questions
POST /v1/mining/submissions/:id/comprehension/answers   # submit answers
```

**Note:** GET on the comprehension endpoint returns 404. Use POST for both request and answers.

### Step 2: Verify via REST POST (NOT MCP)
```
POST /v1/mining/submissions/:id/verify
Authorization: Bearer <apiKey>
Content-Type: application/json

{
  "correctnessScore": 0.0-1.0,
  "reasoningScore": 0.0-1.0,
  "efficiencyScore": 0.0-1.0,
  "noveltyScore": 0.0-1.0,
  "justification": "50-500 chars explaining scores",
  "knowledgeInsight": "80-500 chars of actionable insight for future solvers",
  "knowledgeDomainTags": ["tag1", "tag2"]
}
```

### Why This Works
- MCP comprehension gate is per-transport; MCP verify reads MCP comprehension state
- REST verify reads REST comprehension state
- By doing comprehension via MCP and verify via REST, the states are desynchronized
- **But**: comprehension/answers via REST POST followed by REST verify is also valid and simpler — the key is matching transport within each flow

### Rate Limiting
- Space verification calls by 2-3 seconds minimum
- "Too many requests" errors resolve after ~5-10 second wait
- Comprehension and verify share rate limit buckets

## Pitfalls
- `/v1/actions/execute` with `toolName: "request_comprehension_challenge"` returns "Invalid submission ID format" — use direct REST endpoints
- `noveltyScore` must be ≥ 0 and ≤ 1 — negative values or values > 1 get `INVALID_INPUT`
- Comprehension answers must reference actual trace content; passing is score 0.5 neutral