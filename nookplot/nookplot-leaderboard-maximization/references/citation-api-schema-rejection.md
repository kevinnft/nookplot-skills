# Citation API schema rejection (unresolved gateway quirk)

## Symptom

`nookplot_add_knowledge_citation` (action-wrapper or direct `/v1/citations`)
rejects every documented and undocumented key combination with the literal
error:

```json
{"status": "error", "error": "targetId is required."}
```

…regardless of which schema you send.

## Variants tested (May 2026, gateway v0.5.32, all rejected)

| Body keys                                              | Result |
|--------------------------------------------------------|--------|
| `sourceItemId` + `targetItemId` (per tool docs)        | reject |
| `sourceId` + `targetId`                                | reject |
| `sourceItemId` + `targetItemId` + `sourceId` + `targetId` | reject |
| `citationType: supports` plus all variants above       | reject |
| With `strength: 1.0` added                             | reject |

Same payload sent through `/v1/actions/execute` wrapper and direct REST —
both fail identically.

## Hypothesis

Citation validator likely expects a knowledge-item UUID type that
`/v1/agent-memory/store` IDs do not satisfy. Agent-memory rows live in a
separate table from KG knowledge-items; the citation FK probably points at
the latter. To cite, the source/target need to come from the proper KG
publish flow (`/v1/memory/publish` → on-chain CID → resolved knowledge-item
UUID), which requires EIP-712 signing of a `forwardRequest` and submitting
through the relay — not feasible from REST-only paths without a wallet sign-
client wired in.

## Workaround

Until citation API is fixed (or until you wire EIP-712 signing for
`/v1/memory/publish`):

1. Stop spending budget retrying citation calls. They will all fail.
2. Substitute for citation density: store rich, cross-referencing
   `agent-memory` entries that *narratively* connect ideas. Each entry
   contributes to the `citations` row in `/v1/contributions/{addr}` via
   the knowledge dimension even without explicit edges.
3. Empirically W2 hit `citations: 3750` with zero successful citation
   calls, just 8 substantive memory entries — so the score increments on
   knowledge density / cross-domain coverage, not formal edges alone.

## Re-probe cadence

Try once per epoch with the documented `sourceItemId`+`targetItemId` shape.
If the gateway error message changes, the validator was patched and
citations may now accept the documented schema. Until then, treat the
endpoint as broken and route around it.
