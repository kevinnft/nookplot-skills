# `/v1/exec` E2B chalk bug — May 23 2026

During a W1-W15 maximization push, 2 sandbox exec calls per wallet were attempted via direct REST `/v1/exec` with valid body `{command, image}`. All 30 calls failed with the same gateway/runtime error:

```text
require() of ES Module /app/gateway/node_modules/chalk/source/index.js from /app/gateway/node_modules/e2b/dist/index.js not supported.
```

## Interpretation

This is not a user quota or malformed request issue. It is a gateway dependency/runtime bug in the E2B integration (`chalk` ESM required from a CJS path). Treat exec dim as temporarily blocked until the gateway fixes this dependency or swaps execution backend.

## Operational guidance

- Do not keep retrying `/v1/exec` in a tight loop; it will not move the exec dimension while this error persists.
- Re-probe with a single wallet/no-op before any future exec burst.
- If the single probe succeeds, resume paced exec grinding under the 10 executions/hour/wallet cap.
- If it returns the chalk error, pivot to insights, bounty applications, verification, mining, or KG/citation channels.
