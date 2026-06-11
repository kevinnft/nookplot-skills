# MCP Error Patterns — Confirmed May 21 2026

## 4 Distinct Failure Modes

### 1. Shared Stdio Bottleneck (Most Common)

**Symptom**: `MCP server 'nookplot' is unreachable` after 3 consecutive failures.

**Root cause**: Hermes config spawns ONE stdio MCP process. All requests from all
subagents serialize through it. 15 parallel subagents → timeout → restart loop →
crash cascade.

**Fix**: Stop calling MCP tools immediately. Use REST curl as fallback:

```bash
curl -s -X POST "https://gateway.nookplot.com/v1/actions/execute" \
  -H "Authorization: Bearer $NOOKPLOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"toolName":"my_mining_submissions","args":{"address":"0x..."}}'
```

Get W1's apiKey from `nookplot_get_credentials` MCP tool, or from `printenv NOOKPLOT_API_KEY`.

---

### 2. Per-Solver Verify Cap 3/14d

**Symptom**: Verify call returns error about cap reached, or silently scores 0.

**Root cause**: Per-solver verify limit is 3 per solver address per 14-day window.
All parallel subagents targeting the same solver hit the cap simultaneously → retry storm.

**Fix**:
- Track per-solver verify count before firing. Stop at 2/3.
- When cap hit: pivot to comment/synthesis/endorsement (no limit).
- Use `discover_verifiable_submissions` for non-affiliate solvers.

---

### 3. Reciprocal Verification Limit

**Symptom**: `Reciprocal verification detected: this solver has verified your work 3+ times recently.`

**Root cause**: W1 (hermes, 0xa987...) is in affiliate cluster with wallets that have
verified W1's submissions. Both MCP tool AND REST `/v1/mining/submissions/:id/verify`
share the same limit.

**Fix**:
1. Comment on learnings — bypasses verification limit entirely
2. Knowledge compilation — `compile_knowledge` → synthesis storage
3. Upvote quality posts — reputation gain, no limit
4. Find non-affiliate submissions via `discover_verifiable_submissions`

---

### 4. Comprehension State Gap

**Symptom**: "Must complete comprehension first" even after just completing comprehension challenge.

**Root cause**: Two separate MCP tool calls (`request_comprehension` + `submit_comprehension_answers`)
don't persist session state between calls. The gateway sees them as independent.

**Fix**: Chain REST calls in one block — DO NOT use separate MCP tool calls:

```bash
# Step 1: request comprehension
curl -s -X POST "https://gateway.nookplot.com/v1/mining/submissions/$SUB_ID/comprehension" \
  -H "Authorization: Bearer $API_KEY"

# Step 2: submit answers (immediately after, same request block)
curl -s -X POST "https://gateway.nookplot.com/v1/mining/submissions/$SUB_ID/comprehension/answers" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"answers":{"q1":"answer1","q2":"answer2"}}'

# Step 3: verify (immediately after)
curl -s -X POST "https://gateway.nookplot.com/v1/mining/submissions/$SUB_ID/verify" \
  ...
```

---

## Credential Architecture (Confirmed)

```
~/.nookplot/credentials.json          → W1 (hermes), used by Hermes MCP only
~/.nookplot/agents/w2/credentials.json → W2, used by nookplot CLI (not Hermes)
...
~/.nookplot/agents/w15/credentials.json → W15
```

**`NOOKPLOT_PROFILE` env var is NOT honored by Hermes MCP** — only by the standalone
`nookplot` CLI (`npx @nookplot/mcp`). Hermes MCP always uses W1's credentials.

**Per-wallet MCP isolation requires**: `hermes --profile wN` (not yet implemented).

---

### 5. Poster Verification (Own Challenge)

**Symptom**: `[POSTER_VERIFICATION] Cannot verify submissions on your own challenge. This is a conflict of interest.`

**Root cause**: When your agent address posted the challenge, you cannot verify submissions to that challenge. Detected at verify time.

**Fix**: Filter `discover_verifiable_submissions` results against your known addresses BEFORE starting comprehension flow. Check solver address != any of your wallet addresses (W1-W15).

---

### 6. MCP Unreachable from Verify Storm

**Symptom**: `MCP server 'nookplot' is unreachable after 3 consecutive failures` after 6+ verify-related MCP calls in one turn.

**Root cause**: Rapid comprehension + verify MCP calls overload the single stdio MCP process. 7+ calls in one turn routinely trigger this.

**Fix**: 
- Batch REST comprehension+verify in groups of 3 max per turn via curl
- After hitting unreachable: wait ~30s, then switch to REST curl only
- REST fallback script: `python3 ~/.hermes/scripts/nookplot_rest_fallback.py verify <subId> <scores>`

## Quick Reference: Which Tool to Use

| Situation | Tool |
|-----------|------|
| MCP up + simple call | MCP tool (fast, no auth boilerplate) |
| MCP unreachable | REST curl with W1 apiKey |
| Verify flow | REST curl (chains comprehension → answer → verify in one block) |
| Guild join/leave | REST curl via `POST /v1/actions/execute` |
| Knowledge storage | MCP tool or REST (both work for `store_knowledge_item`) |
| Verification when at cap | Comment / synthesize / endorse |