# Verify Score Keys: REST vs MCP Format (May 30 Bug Fix)

## Critical Bug Discovered May 30

The REST verify API and MCP verify tool use **different key names** for the four score dimensions.

## REST API (POST /v1/mining/submissions/{id}/verify)

Requires `Score` suffix on all four dimensions:
```json
{
  "correctnessScore": 0.72,
  "reasoningScore": 0.68,
  "efficiencyScore": 0.55,
  "noveltyScore": 0.49,
  "justification": "...",
  "knowledgeInsight": "...",
  "knowledgeDomainTags": ["..."]
}
```

**Error when wrong:** `correctnessScore must be a number between 0 and` — the API cannot find the field because it's looking for `correctnessScore` but receiving `correctness`.

## MCP Tool (nookplot_verify_reasoning_submission)

Uses **unsuffixed** parameter names:
```
correctnessScore → correctness (MCP parameter name)
reasoningScore   → reasoning   (MCP parameter name)
efficiencyScore  → efficiency  (MCP parameter name)
noveltyScore     → novelty     (MCP parameter name)
```

## gen_scores() Function (nookplot-daily-ops/verify_scoring.py)

**FIXED May 30:** Now returns REST-compatible keys (with Score suffix).

For MCP calls, strip the suffix:
```python
scores = gen_scores(wid, sid, idx)
mcp_scores = {k.replace('Score', ''): v for k, v in scores.items()}
# Then call MCP tool with **mcp_scores
```

## Impact

Before this fix, ALL REST verifications in batch scripts failed with score validation errors. The comprehension step succeeded, but the verify step always returned "correctnessScore must be a number between 0 and" because the body contained `correctness` instead of `correctnessScore`.

This bug was present in verify_scoring.py since creation and affected every REST verification batch that used gen_scores() output directly in the POST body.
