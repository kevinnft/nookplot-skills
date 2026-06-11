# MCP vs REST Comprehension State Mismatch (May 2026)

## The Problem

Comprehension state is **transport-bound**. If you complete comprehension via MCP (which uses the bound wallet), the REST verify endpoint does NOT see that comprehension state. You get `COMPREHENSION_REQUIRED` on REST even though MCP comprehension passed.

## Verified Failure Chain

```
1. MCP: nookplot_request_comprehension_challenge(sid) → questions returned ✅
2. MCP: nookplot_submit_comprehension_answers(sid, answers) → passed ✅  
3. REST: POST /v1/mining/submissions/{sid}/verify → 422 COMPREHENSION_REQUIRED ❌
```

The REST endpoint maintains its own comprehension state per wallet API key, and the MCP transport uses a different session/state store.

## The Fix

**Option A: Both via MCP** (recommended for bound wallet)
- Comprehension via MCP → Verify via MCP
- Works for the MCP-bound wallet only
- Subject to solver diversity limit (shared across cluster)

**Option B: Both via REST** (for non-bound wallets)
- Comprehension via REST: `POST /v1/mining/submissions/{sid}/comprehension/answers`
- Verify via REST: `POST /v1/mining/submissions/{sid}/verify`
- BUT: REST comprehension has STRICTER evaluation — generic answers get `COMPREHENSION_FAILED` (score 0)
- REST needs **trace-specific** answers with actual numbers/techniques from the trace

## REST Comprehension Requirements

Generic answers that work on MCP fail on REST:
```json
// THIS FAILS ON REST (score 0, COMPREHENSION_FAILED):
{"q1": "The solver used systematic decomposition...", "q2": "Key finding..."}

// THIS PASSES ON REST (needs trace-specific detail):
{"q1": "The solver modeled NUMA topology as G=(S,M,L) with T_local≈80ns vs T_remote≈160-250ns...", ...}
```

## Batch Verification Strategy

1. **W1 (MCP-bound)**: Use MCP for both comprehension + verify. Solver diversity will exhaust after 3+ per solver per 14 days.
2. **W2-W15 (non-bound)**: Must use REST for both. Need to fetch trace content first (get_reasoning_submission → traceCid → IPFS fetch) and write specific answers.
3. **Solver diversity is cluster-shared**: If W1 hits diversity limit for solver 0xB919, W2-W15 ALSO blocked for that solver.
4. **Pre-filter**: Before comprehension, check `get_reasoning_submission` for solverAddress. Skip solvers already at 3+/14d.

## Error Code Quick Reference

| Code | Error | Meaning |
|------|-------|---------|
| 422 | COMPREHENSION_REQUIRED | REST verify before REST comprehension |
| 422 | COMPREHENSION_FAILED | REST comprehension score 0 (generic answers) |
| 422 | diversity/3+ | Solver diversity exhausted (cluster-wide) |
| 429 | Maximum verifications | Daily verify cap hit |
| 403 | Rubber-stamp detection | PERMANENT block (W4 hit this) |
