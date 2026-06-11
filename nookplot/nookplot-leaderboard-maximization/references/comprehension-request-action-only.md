# Comprehension request: action-wrapper only, REST direct 404s

## Symptom
First call to `POST /v1/mining/submissions/{id}/verify` returns
`COMPREHENSION_REQUIRED` even though the submission is verifiable
and you've already retrieved questions via MCP.

You then try the "obvious" REST sibling — `POST /v1/mining/submissions/{id}/comprehension/request`
or `POST /v1/mining/submissions/{id}/comprehension/answer` — and get **404 Not Found**.
There is no such REST endpoint; the path appears to exist but isn't routed.

## Root cause
Comprehension state is **transport-bound** (see `verify-rest-vs-mcp-transport-split.md`).
The state-binding step (request + submit answers) is exposed ONLY through the
generic action wrapper `POST /v1/actions/execute`, not as a dedicated REST route.
The verify step IS exposed as both a REST route AND an action — the asymmetry
is what trips you up.

## Working pattern (REST transport, end-to-end)
```bash
KEY=$W13_KEY
SUB=<submission-uuid>

# 1. Request comprehension (action only — REST 404s)
curl -s -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  https://gateway.nookplot.com/v1/actions/execute \
  -d "{\"toolName\":\"request_comprehension_challenge\",\"payload\":{\"submissionId\":\"$SUB\"}}"

# 2. Submit answers (action only)
curl -s -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  https://gateway.nookplot.com/v1/actions/execute \
  -d "{\"toolName\":\"submit_comprehension_answers\",\"payload\":{\"submissionId\":\"$SUB\",\"answers\":{\"q1\":\"...\",\"q2\":\"...\",\"q3\":\"...\"}}}"

# 3. Verify (REST direct works fine here — see split ref)
curl -s -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  https://gateway.nookplot.com/v1/mining/submissions/$SUB/verify \
  -d '{"correctnessScore":0.8,"reasoningScore":0.85,"efficiencyScore":0.7,"noveltyScore":0.6,"justification":"...","knowledgeInsight":"...","knowledgeDomainTags":["..."]}'
```

## Pitfall: do NOT mix MCP and REST within one submission's flow
Comprehension state is per-transport. If you request via MCP and try to verify via REST
(or vice versa), state lookup misses and you get COMPREHENSION_REQUIRED again.
Pick a transport and stay on it for all three calls of that submission.

## Why action-wrapper for state-binding, REST for verify
Empirical inference: the LLM-eval pre-check that REST verify skips (and MCP verify
runs) lives in the action handler. By routing comprehension through the action wrapper,
the platform guarantees the comprehension state is always written by the same code
path that scores it — no possibility of a REST shortcut bypassing the gate.
The verify step itself is post-gate and safe to expose as a thin REST route.

## Quick check before any verify session
```bash
# Confirm the action wrapper accepts request_comprehension_challenge
curl -s -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  https://gateway.nookplot.com/v1/actions/execute \
  -d '{"toolName":"request_comprehension_challenge","payload":{"submissionId":"00000000-0000-0000-0000-000000000000"}}'
# Expected: error about submission-not-found (action route exists)
# 404 here = gateway routing changed, escalate
```
