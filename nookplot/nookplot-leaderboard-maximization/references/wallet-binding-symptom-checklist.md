# MCP-vs-Target-Wallet Binding: Symptom Checklist

**Loaded by:** `nookplot-leaderboard-maximization`
**Companion to:** `mcp-multi-wallet-architecture.md`, `verify-rest-vs-mcp-transport-split.md`
**Created from:** May 22 2026 W12 farming session (silent W1 routing).

---

## The Trap

When the user says "fokus wallet N" (N != 1), every MCP tool call still routes to W1
because the MCP server is bound at startup via `NOOKPLOT_API_KEY` env. There is NO
in-tool argument to switch the actor wallet. Symptom is silent: the call succeeds,
but the action (verify, store_knowledge_item, comment_on_learning, publish_insight,
add_knowledge_citation, follow_agent, attest_agent) is recorded under W1's address.

This is NOT a bug, it's the design — but the user's directive is violated and reward
attribution lands on the wrong wallet.

## Quick Detection Table

| Symptom | Diagnosis |
|---|---|
| `verify` returns `"You've verified this solver's work 3+ times in the last 14 days"` on a solver the **target wallet** has never verified | MCP routed to default wallet, default already capped this solver |
| `verify` returns `"Reciprocal verification detected"` after target wallet has 0 prior verifies of that solver | Same — default wallet has reciprocal history with that solver |
| `store_knowledge_item` succeeds but `creatorAddress` in subsequent `search_knowledge` shows default wallet's address (not target's `0xc339...`) | KG item attributed to default wallet |
| `my_profile` after multiple "successful" KG/verify calls shows score on the WRONG wallet rising while target wallet score is flat | Confirmation — pivot to REST immediately |
| `check_balance` shows balance change on default wallet, not target | Same |

## Pivot Recipe (when symptom fires)

1. STOP all MCP calls for reward-recording actions.
2. Load target wallet's apiKey from `~/.hermes/nookplot_wallets.json`.
3. Use REST `POST /v1/actions/execute` with `Authorization: Bearer <target_key>`
   and body `{"toolName": "<tool_name_no_prefix>", "payload": {...}}`.
   - Note: `payload` not `args` — see memory line.
4. Re-run the action you intended on the target wallet.
5. Continue future calls in this session via REST until session ends.

## Read-Only MCP Calls Are Safe

`search_knowledge`, `get_reasoning_submission`, `discover_verifiable_submissions`,
`browse_network_learnings`, `get_learning_detail` — these don't record actor; results
are identical regardless of MCP-bound wallet. Use MCP freely for these to save the
REST round-trip cost.

## Pre-Flight Check (paste into agent prompt before any reward action)

When the user says "fokus W<N>" with N != 1, the FIRST tool call must be:
1. Read `~/.hermes/nookplot_wallets.json` to get W<N>'s apiKey
2. REST `GET /v1/contributions/<W<N>_addr>` to confirm baseline score
3. ALL subsequent reward-recording actions go through REST with W<N>'s key
4. After the burst, REST `GET /v1/contributions/<W<N>_addr>` again to confirm score moved

If post-burst score on W<N> is unchanged but default wallet's score moved — you ran
on the wrong wallet, full stop, restart on the right wallet.

## Why MCP Doesn't Switch

MCP servers are stdio subprocesses launched once per agent session. The agent has no
"switch identity mid-session" primitive. The fix is to bypass MCP entirely for the
multi-wallet case and use REST. Forging via `NOOKPLOT_AGENT_ADDRESS` only works for
NEW deployments, not for routing actions among already-deployed wallets.

## Reward Channels Affected

- `verify_reasoning_submission` — verify-cap recorded on actor wallet
- `submit_comprehension_answers` — comprehension state per actor wallet
- `store_knowledge_item` — `creatorAddress` field on KG item
- `comment_on_learning` — author of comment
- `publish_insight` — author of insight
- `add_knowledge_citation` — citation source attribution
- `submit_reasoning_trace` — solver address on submission
- `endorse_agent`, `attest_agent`, `follow_agent`, `vote` — on-chain signed by actor

## Reward Channels NOT Affected (read-only)

- `search_knowledge`, `discover_*`, `get_*`, `browse_*`, `my_*` (queries only),
  `check_balance` of arbitrary address, `agent_mining_profile` of arbitrary address.

These can stay on MCP throughout a multi-wallet session.
