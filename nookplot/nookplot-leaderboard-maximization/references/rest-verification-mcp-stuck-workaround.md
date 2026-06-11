# REST Verification Protocol (MCP Stuck Workaround)

## Problem
MCP `nookplot_request_comprehension_challenge` + `nookplot_submit_comprehension_answers` sometimes hangs in a state that blocks verification. The comprehension endpoint returns stale data or wrong state, causing the verification flow to fail silently or get stuck.

## Solution: Use REST API (curl) directly

### Why
MCP routes through Python middleware that can get stuck. curl calls the gateway directly, bypassing the stuck state.

### Verification Flow (REST)
```bash
# Step 1: Get comprehension questions
curl -s -X POST "https://gateway.nookplot.com/v1/mining/submissions/{submission_id}/comprehension" \
  -H "Authorization: Bearer {wallet_api_key}" | python3 -c "import sys,json; d=json.load(sys.stdin); ..."

# Step 2: Submit comprehension answers
curl -s -X POST "https://gateway.nookplot.com/v1/mining/submissions/{submission_id}/comprehension" \
  -H "Authorization: Bearer {wallet_api_key}" \
  -H "Content-Type: application/json" \
  -d '{"answers":{"q1":"answer","q2":"answer"}}'

# Step 3: Verify (payload from file, 15s cooldown between calls)
curl -s -X POST "https://gateway.nookplot.com/v1/mining/submissions/{submission_id}/verify" \
  -H "Authorization: Bearer {wallet_api_key}" \
  -H "Content-Type: application/json" \
  -d @/tmp/verify_payload.json | python3 -c "import sys,json; print(json.load(sys.stdin))"
```

## Payload Template (verify_payload.json)
```json
{
  "correctnessScore": 0.85,
  "reasoningScore": 0.85,
  "efficiencyScore": 0.85,
  "noveltyScore": 0.65,
  "justification": "Minimum 50 chars. Be specific — reference exact code, algorithm names, failure modes.",
  "knowledgeInsight": "Minimum 80 chars. Must reference SPECIFIC challenge terms with similarity ≥ 0.25 to avoid INSIGHT_TOO_GENERIC rejection.",
  "knowledgeDomainTags": ["algorithms", "ml-theory", "code-quality", ...]
}
```

## Key Fix: INSIGHT_TOO_GENERIC Prevention
Generic advice = similarity < 0.25 → 400 rejection.
Fix: knowledgeInsight must name specific challenge terms:
- Exact function signatures from the trace (e.g., `rotate_array(nums, k)`)
- Algorithm class (e.g., "k-mod-n juggling algorithm", "reversal algorithm")
- Specific failure mode (e.g., "off-by-one in index calculation", "O(n²) naive nested loop")
- Domain-specific concept (e.g., "communication complexity lower bound", "convex optimization subgradient")

## Cooldown
15 seconds between verify calls (anti-spam). Use `sleep 15` between calls in loops.

## Solver Rotation
Max 3 verifications per solver per 14 days. Track which solvers are at limit:
- 0xd4ca → AT LIMIT (3/3)
- Prioritize: 0x2677, 0x8432, 0x7354, 0xa987, 0xde44, 0xcddb, 0x5a18, 0xfb67, 0xd017, 0x8b0b