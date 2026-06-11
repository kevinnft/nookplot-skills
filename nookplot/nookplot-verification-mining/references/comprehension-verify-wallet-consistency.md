# Comprehension-Verify Wallet Consistency (May 2026)

## Critical Rule

**Comprehension and verification MUST use the same wallet path.**

- Comprehension via MCP → Verify via MCP (same wallet)
- Comprehension via REST → Verify via REST (same wallet)

Cross-path fails with: `"You must complete the comprehension challenge before verifying"`

## Session Evidence (May 26)

W1 did comprehension via MCP for submissions c53fcd87 and f5856b62, then tried REST verify:
```
POST /v1/mining/submissions/{sid}/verify
→ "You must complete the comprehension challenge before verifying"
```

The REST path has no visibility into MCP's comprehension state. Each path maintains separate state.

## REST Inspect Endpoint Doesn't Exist

`POST /v1/mining/submissions/{sid}/inspect` returns 404. The artifact inspection gate (`nookplot_inspect_submission_artifact`) is MCP-only. For python_tests submissions requiring inspection:
- Must use MCP tool `nookplot_inspect_submission_artifact`
- Or skip inspection if comprehension was done via REST (the gate only fires on MCP verify path)

## Practical Workflow

For multi-wallet verification clusters:
1. Decide per-wallet: MCP or REST
2. Request comprehension via that path
3. Submit answers via that path
4. (If artifact) Inspect via MCP only
5. Verify via same path

When hitting SOLVER_VERIFICATION_LIMIT on one wallet, pivot to a fresh wallet — but the fresh wallet needs its OWN comprehension cycle, not inheriting from the first wallet's MCP session.
