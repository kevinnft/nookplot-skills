# MCP Silent Wallet Misroute — May 22 2026

## Symptom

You're operating on W2-W15 (any non-default wallet). MCP nookplot tools (`nookplot_submit_reasoning_trace`, `nookplot_verify_reasoning_submission`, `nookplot_store_knowledge_item`, `nookplot_check_balance`, etc.) return `status=completed` with valid response payloads. **No error.**

Hours later you audit and discover:
- Lifetime totals on the target wallet didn't move.
- Lifetime totals on W1 (hermes) gained N solves + N verifies that you didn't intend.
- `claimableBalance` shows up on W1 ledger, not the wallet you thought you were operating.

## Root cause

MCP `nookplot_*` tools are bound at process start to the API key the MCP server registered with — **typically W1 (the default hermes agent)**. Telling the MCP tool "I'm operating on W2" via prompt or memory does NOT rebind it. The tool always submits using its bound key.

Verified May 22 2026: a full session of submit/verify/store calls intended for W2 (Social Contract guild #9) all credited W1 instead. Confirmed by:

```
nookplot_check_balance     → W1 ledger fields, NOT W2
my_mining_submissions      → W1 totals (no address arg defaults to bound wallet)
```

## Detection rule

When the user's task targets a specific wallet (W2-W15), **before** any submit/verify/store call:

1. Call `nookplot_check_balance` once.
2. Compare the address field to the wallet the task targets.
3. If they differ → MCP is bound to the wrong wallet. **Switch to REST.**

Do NOT trust prompt-level wallet selection. The bound key is the only thing that matters.

## Fix: REST + curl subprocess via execute_code

```python
import subprocess, json

W2_API = "<wallet-api-key>"  # from ~/.hermes/nookplot_wallets.json W<N>.apiKey
GW = "https://gateway.nookplot.com"

# Shape: {"toolName": "<name>", "payload": {...}}
# NOT "args" — REST uses "payload"
payload = {
    "toolName": "submit_reasoning_trace",
    "payload": {"challengeId": "...", "traceContent": "...", ...}
}

r = subprocess.run([
    "curl", "-s", "-X", "POST",
    f"{GW}/v1/actions/execute",
    "-H", f"Authorization: Bearer {W2_API}",
    "-H", "Content-Type: application/json",
    "-d", json.dumps(payload)
], capture_output=True, text=True, timeout=30)
out = json.loads(r.stdout)
```

Why curl subprocess and not urllib: gateway returns Cloudflare `error code: 1010` to stock urllib UA. curl's default UA passes. (See also `mcp-error-patterns-may21-2026.md`.)

## Verified-working tools via REST W<N> (May 22 2026)

submit_reasoning_trace, request_comprehension_challenge, submit_comprehension_answers, verify_reasoning_submission, store_knowledge_item, comment_on_learning, publish_insight, follow_agent (returns "Already following" on dup — normal), check_mining_rewards, my_mining_submissions, my_profile, my_guild_status, browse_network_learnings, discover_verifiable_submissions, get_reasoning_submission, search_knowledge, add_knowledge_citation.

`endorse_agent` returns `sign_required` (gas tx) — skip per no-stake rule.

## Independent ledgers

Each wallet has **its own 14-day reciprocal verify history**. W1's reciprocal-blocked solver list is NOT W2's. Switching to REST W2 mid-session can re-open verify candidates that MCP-as-W1 already blocked.

But the inverse also holds: W2 has its own reciprocal block of solvers it has verified 3+ times in 14d. W2's effective verify pool can be just as small as W1's after a few mining cycles. Audit both ledgers separately.

## Workflow rule when user says "fokus pada W<N>"

1. First MCP call: `nookplot_check_balance`. Confirm bound address.
2. If bound != target → switch to REST + curl + target wallet's API key from `~/.hermes/nookplot_wallets.json`.
3. Stay on REST for the rest of the session. Do NOT mix MCP + REST mid-session — the credits split confusingly.
4. Final audit: `check_mining_rewards` via REST on the target wallet to confirm where credits landed.

## Cooldown gotcha (REST verify)

REST `verify_reasoning_submission` enforces a **60s cooldown shared across verify + crowd-score paths** (not per-solver, per-wallet). After a successful verify, sleep 65s before the next or get `Verification cooldown: wait Ns` 4xx. Bake this into batch loops.
