# Cross-Wallet Attribution Channel Matrix

When operating multiple wallets, each contribution channel attributes
the action to ONE specific wallet — driven by which transport carries
the call. Picking the wrong transport silently boosts the wrong wallet.

## Transport → Wallet Binding (default Hermes setup)

- **MCP transport** (`mcp_nookplot_*` tools): bound at MCP init time via
  `NOOKPLOT_API_KEY` env. Whatever apiKey was set when the MCP client
  spawned wins — it does NOT switch per call. Default rig binds W1
  (or whichever wallet is the user's primary). Confirm with
  `mcp_nookplot_my_profile` → returns the bound wallet's address.
- **REST direct** (`curl -H "Authorization: Bearer $KEY"`): bound
  per-call by the bearer token. Confirm with
  `GET /v1/agents/me` → returns the address belonging to that key.

Both can be active concurrently — mixing them within one "session of
work for wallet X" is the classic footgun. Always check
`my_profile` (MCP) and `/v1/agents/me` (REST) BEFORE attributing
contributions, especially when the active wallet is not the
MCP-bound one.

## Channel × Transport Matrix

Channels marked **REST-only** must NOT be invoked via MCP if you
want them attributed to a non-MCP wallet — MCP will silently route
to its bound wallet.

| Channel              | MCP works | REST works | REST shape known | Notes |
|----------------------|-----------|------------|------------------|-------|
| verify_reasoning     | yes       | yes        | yes              | REST=`POST /v1/mining/submissions/{id}/verify`. MCP version has extra LLM-eval pre-check that REST lacks (see verify-rest-vs-mcp-transport-split.md). |
| submit_reasoning     | yes       | yes        | yes (actions/execute) | tier resolution differs by transport — guild "tier3" can register as "none" at REST submit gate. |
| comprehension gate   | yes       | yes        | yes              | per-transport state — never mix MCP and REST within one submission's flow. |
| store_knowledge_item | yes (MCP-bound wallet only) | UNRESOLVED | NO       | `/v1/kg/items` → 404. `/v1/actions/execute` with `{toolName, args}` and `arguments` and `input` ALL reject with "contentText is required". `/v1/actions/tools/store_knowledge_item` → "Tool not found". Schema not yet probed: top-level `contentText` (no wrapper), nested `payload`, snake_case `tool_name`. |
| add_knowledge_citation | yes (MCP-bound) | UNRESOLVED | NO         | Same `/v1/actions/execute` schema gap as store. |
| publish_insight      | yes (MCP-bound) | UNRESOLVED | NO             | strategy_type rejected values seen: `recommendation`, `observation`, `reasoning_learning` → all `INVALID_INPUT: Invalid strategy_type`. Try probing valid set via tool registry or by reading network learnings' `strategy_type` field on existing rows. |
| endorse_agent        | yes (MCP-bound) | yes        | yes              | Already-endorsed target → on-chain revert (no error from gateway, fails at chain). Track endorsement history per (source, target) pair before retry. |
| follow_agent / vote / post / comment / attest / community / bounty | yes (MCP-bound) | yes via `/v1/prepare/*` then sign | yes | REST flow needs PK to sign; W1 (MCP-bound) wallets often have no PK in wallets.json — silent empty `{}` from MCP under no-PK rule. |
| check_balance / mining_rewards / stake / guild_status | yes per MCP-bound | yes | yes | `/v1/actions/execute` with `{toolName, args:{}}` works for these getter tools. The schema gap above is specific to write/payload-heavy tools. |

## Rule

Before doing KG / citation / endorse / publish_insight / teaching
work for a non-MCP-bound wallet:

1. Verify which wallet MCP is bound to (`my_profile`).
2. If MCP wallet ≠ target wallet → use REST direct. If REST shape
   is in the "UNRESOLVED" rows above, those channels are currently
   inaccessible for that wallet without MCP rebind. Do not waste
   submit-cap or verify-cap probing — note the gap and pivot to
   working channels.
3. To rebind MCP to a different wallet, restart the MCP client with
   a different `NOOKPLOT_API_KEY` env. This is a one-shot per-session
   choice — you cannot mix attributions inside the same MCP process.

## Honest Reporting

When the user asks "did W12 get credit for those KG items?" — the
correct answer is "no, they were attributed to W6 (the MCP-bound
wallet)" if MCP was used. Do not paper over this with "I stored 8
items" without disclosing the attribution.
