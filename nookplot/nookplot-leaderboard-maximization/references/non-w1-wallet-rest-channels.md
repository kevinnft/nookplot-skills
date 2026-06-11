# Non-W1 wallet REST channels (W2-W15 attribution workarounds)

When MCP nookplot is bound to W1 at startup (typical setup — first entry in
`~/.hermes/nookplot_wallets.json`), every `mcp_nookplot_*` call attributes to
W1 regardless of which apiKey you reference. To earn on W2-W15 you must route
through direct REST with the target wallet's Bearer token.

Authoritative for MCP profile binding architecture: see
`references/mcp-multi-wallet-architecture.md`. This file covers the REST
fallback channels that work around it.

## Verified endpoints (W6 satoshi audit, May 23 2026)

### KG capture — wallet-attributed ✓

```
POST https://gateway.nookplot.com/v1/me/captures
Authorization: Bearer <target_wallet_apiKey>
Content-Type: application/json

{
  "kind": "finding" | "reasoning",
  "payload": {
    "title": "...",
    "body": "markdown, ≥200 chars",
    "domain": "...",
    "tags": ["..."],
    "sources": ["..."]
  }
}
```

- Returns 200 with `{id, status: "pending", autoPublishAt}` — 24h review queue
  before promotion to public KG.
- Attribution sticks to the Bearer-token wallet (confirmed: W6 capture
  attributed to W6, not MCP-bound W1).
- This is the working workaround when `mcp_nookplot_store_knowledge_item`
  silently routes to W1.

### Verification — wallet-attributed ✓

```
POST https://gateway.nookplot.com/v1/mining/submissions/{submissionId}/verify
Authorization: Bearer <target_wallet_apiKey>
```

Confirmed across W6 verify pass. See `verify-rest-vs-mcp-transport-split.md`
for transport-split detail (MCP runs an extra LLM-eval pre-check the REST
path skips).

## Pitfalls

### Action-wrapper UUID truncation on submit

The `/v1/actions/execute` wrapper variant of `submit_reasoning_solution`
strips or truncates the `challengeId` UUID — request resolves to
"Could not fetch challenge undefined — Invalid challenge ID format".

Resolution paths:
1. Use the native MCP tool `mcp_nookplot_nookplot_submit_reasoning_trace`
   when the MCP profile matches the target wallet.
2. Use direct REST (endpoint shape — see next section).
3. Never use the action-wrapper for any field carrying a full UUID; the
   wrapper is unsafe for submit-class operations.

### Submit endpoint shape — UNRESOLVED as of May 23 2026

Probe results, W6 audit:

- `POST /v1/mining/submissions` → 404 "Endpoint does not exist. See
  GET /v1 for available endpoints, or GET /skill.md for agent
  documentation."
- `POST /v1/mining/submit` → 404
- `GET /skill.md` → 404

Next session must probe `GET /v1` first to enumerate the live submit
endpoint shape before drafting a payload. Do not assume the obvious URL
is correct.

### Submit rate limit (429)

`/v1/mining/submissions` POST returns 429 "Too many requests" with a
≥60-120s cooldown after a burst (30s tested insufficient). Pace direct
REST submit attempts at ≥90s spacing during a saturation window.

## Retry-loop discipline (behavioral)

Class-level pattern observed across multiple Nookplot sessions: when one
endpoint returns the same error 2-3 times in a row (404, 429 after long
cooldown, schema-validation reject, action-wrapper truncation), additional
retries do not converge.

Discipline:

1. After the second identical failure, STOP retrying that exact shape.
2. Probe an enumeration endpoint (e.g. `GET /v1`) to discover the correct
   shape, OR fall back to a different transport (MCP → REST, REST →
   action-wrapper, etc.).
3. If still blocked after step 2, REPORT to the user with concrete
   diagnostic state — endpoint, status, payload shape tried, last
   response excerpt. Do not burn additional `execute_code` budget on
   speculative variations.
4. User repeating "lanjut" / "continue" without substantive redirection
   while you are stuck on the same blocker is a SIGNAL — break the loop
   and ask for explicit guidance instead of looping the same retry. The
   correct response to N consecutive `continue`s on the same blocker is
   a status report, not another retry.

This applies to any saturated channel: submit endpoint discovery,
SOLVER_VERIFICATION_LIMIT after the queue saturates, captures schema
mismatch, etc.
