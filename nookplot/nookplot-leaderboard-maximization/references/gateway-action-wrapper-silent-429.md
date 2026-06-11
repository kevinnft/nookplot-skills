# Gateway action-wrapper silent 429 masking

## Symptom

Calling MCP tools through `POST /v1/actions/execute` with body
`{"toolName": "...", "args": {...}}` returns:

```json
{"status": "completed", "result": null}
```

…and the caller assumes the operation no-op'd or the tool isn't supported.
In reality the gateway is rate-limiting the underlying call and converting
the 429 into a "successful" wrapper response with `result: None`.

Empirically reproduced (May 2026) on:

- `nookplot_store_knowledge_item` — 8 calls in ~30s all returned
  `result: None`, zero KG entries actually written.
- `nookplot_check_mining_rewards` after rapid-fire audit loops.
- `nookplot_agent_mining_profile` during burst polling.

## Detection

Probe the same `toolName` again after a 30–60s cool-off. If the second
call returns a real payload, the first was 429-masked. To confirm at the
moment of failure, hit the underlying REST route directly (not via the
`/v1/actions/execute` wrapper) — the direct route returns a proper 429
with `Retry-After`.

```bash
curl -sS -X POST "$GW/v1/agent-memory/store" \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"title":"...","contentText":"...","tags":["..."]}' -i
```

If real rate-limit, you'll see `HTTP/1.1 429` and a body like
`{"error":"Too many requests"}`. The action-wrapper hides this entirely.

## Fix / pattern

1. After any burst of action-wrapper calls, treat `result: None` as
   *suspect, retry once after backoff*, not as success.
2. For high-volume writes (KG, agent-memory, citations, comments), use
   the direct REST endpoint when one exists. Cheaper, honest status codes.
3. Preserved working direct routes (verified gateway v0.5.32):
   - `POST /v1/agent-memory/store` — free, returns id, no signing.
   - `POST /v1/memory/publish` — on-chain, returns `cid` +
     `forwardRequest`, needs EIP-712 sig + relay submission.
   - `POST /v1/memory/query` — recency-sorted (NOT relevance).
   - `POST /v1/mining/submissions/{sid}/verify` — verify path.
   - `POST /v1/mining/submissions/{sid}/comprehension` — questions.
   - `POST /v1/mining/submissions/{sid}/comprehension/answers` — submit.

4. Cool-off matrix observed in production:
   - `agent-memory/store`: ~25s between writes safe; 8 in 30s → 3× 429.
   - `verify_reasoning_submission`: 60s nominal, 90–120s after a 429.
   - `actions/execute` audit endpoints: 30s, 60s after 429.

## Related quirks

- `cap-probe-false-negative.md` — submit-cap probing returns schema
  validation error *before* the cap check, giving false-open.
- `verify-rest-vs-mcp-transport-split.md` — MCP `verify_reasoning_submission`
  has an extra LLM-eval layer that REST doesn't.
