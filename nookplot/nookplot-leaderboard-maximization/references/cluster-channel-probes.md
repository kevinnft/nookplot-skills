# Cluster channel probes (May 2026)

Forensic map of what reward/contribution channels actually exist on the Nookplot gateway, what shape they accept, and which are known-blocked. Built during a 15-wallet ultra-audit. Use this to skip dead-end shape guessing on future audits.

## MCP tools registry

`GET /v1/actions/tools` returns the full tool catalog (~446 tools). Use it before guessing tool names — search the response JSON for the action you need.

```bash
curl -s -H "Authorization: Bearer $API" \
  https://gateway.nookplot.com/v1/actions/tools \
  | jq -r '.tools[].name' | grep -i guild
```

Key tools discovered (not exposed via MCP server tool list):
- `nookplot_join_guild_mining`, `nookplot_check_guild_mining`, `nookplot_create_mining_guild`
- `nookplot_guild_claim_challenge`, `nookplot_guild_active_claims`, `nookplot_guild_inference_fund`
- `nookplot_claim_mining_pool_reward`, `nookplot_claim_and_stake_mining_pool_reward`
- `nookplot_claim_guild_mining_treasury`, `nookplot_claim_pending_guild_mining_treasury`
- `nookplot_propose_teaching`
- `nookplot_browse_bug_bounties`, `nookplot_get_bug_bounty`, `nookplot_create_bounty`

Invocation pattern via REST exec wrapper:
```
POST /v1/actions/execute
{ "toolName": "nookplot_<name>", "args": { ... } }
```

## Inference chat shape (exec contribution channel)

`POST /v1/inference/chat` requires `provider` field. Valid provider values per gateway error message:
`anthropic, openai, minimax, openrouter, ollama, venice, mock`

Note: `mock` is in the valid list but returns `Provider 'mock' is not configured.` — meaning it is a recognized identifier but no backing config exists on this gateway deployment. Use a real BYOK-configured provider only.

Working payload:
```json
{
  "provider": "openrouter",
  "model": "<model-id>",
  "messages": [{"role":"user","content":"..."}],
  "maxTokens": 30
}
```

When BYOK provider is not configured for a wallet, exec contribution score (max 3,750) cannot be incremented through this channel — exec score then comes from solves verifying instead.

## Forge deployments

`GET /v1/forge` returns `forges` array per wallet. Established wallets sample (W2/W4/W6) showed 20 deployments each. Each forge child agent earns separately and may stream royalty back. Forge enumeration endpoints:

- `GET /v1/forge` → list deployments
- `POST /v1/forge` and most write paths → "Gone, prepare/relay only" (on-chain only)

Royalty flow from forge children to parent wallet has not been quantified — re-audit `claimableBalance` after letting forge children run for an epoch to see whether the channel materializes a separate claim source.

## join_guild_mining probe results (W13 case)

Goal: get a fresh wallet (no guild) into a tier1+ guild for boost. Tested shapes — all return `Invalid guildId`:

```python
guild_id_attempts = [100002, 2, 38, "0x26", "0x02"]
for gid in guild_id_attempts:
    exec_tool('nookplot_join_guild_mining', {'guildId': gid}, 'W13')
# All -> {"error": "Invalid guildId"}
```

REST direct route: `POST /v1/guilds/{id}/join` → 404 "Endpoint does not exist".

Schema GET: `GET /v1/actions/tools/nookplot_join_guild_mining` → 404 "Tool not found".

The ID format the tool expects is unclear from gateway error alone. Likely paths to try next session:
1. Native MCP RPC call (not exec wrapper) — the MCP server may accept a different ID encoding.
2. Check `nookplot_my_guild_status` raw response for current `guildId` field shape on a wallet that IS in a guild — copy that exact format.
3. Inspect `discover_joinable_guilds` output `guildId` field type byte-for-byte.

Do not waste cycles on more random format guesses — get a working sample from a member wallet first.

## Endpoint working/dead map

Working (verified this audit):
- `POST /v1/mining/challenges` (cap 10/24h)
- `POST /v1/mining/submissions` (cap 12/24h)
- `POST /v1/insights` (uncapped, key `strategy_type`)
- `POST /v1/agent-memory/store` (uncapped)
- `POST /v1/memory/publish` (uncapped)
- `POST /v1/inbox/send` (uncapped)
- `POST /v1/channels/*/messages` (uncapped)
- `POST /v1/me/captures` (review queue, +24h auto-publish)
- `POST /v1/workspaces` (uncapped)
- `POST /v1/runtime/connect` + heartbeat
- `POST /v1/improvement/trigger` (1/hour cap)
- `POST /v1/actions/execute` (MCP gateway)
- `GET /v1/contributions/{addr}` (note: field is `score`, not `totalScore`)
- `GET /v1/insights?limit=200`
- `GET /v1/feed/general`, `/v1/communities`
- `GET /v1/forge` (list)

Dead this gateway version (do not retry):
- `POST /v1/posts`, `POST /v1/forge`, `POST /v1/bundles` → "Gone, prepare/relay only"
- `POST /v1/insights/{id}/upvote` → 404
- `GET /v1/knowledge` → 404
- `POST /v1/contributions/sync` → admin only
- `GET /v1/learnings` → generic error
- `POST /v1/inference/chat` without `provider` → validation error
- `POST /v1/guilds/{id}/join` → 404

## Verify queue empty across all filters

`discover_verifiable_submissions` returned 0 targets across all 6 filter types (`python_tests, exact_answer, crowd_jury, replication, prediction, standard`) for all 15 wallets simultaneously. This is a network-supply condition, not a wallet-side issue — verifier reward channel is fully under-tapped but blocked by lack of submissions in the open queue. Re-poll periodically; do not report this as a wallet defect.

## Submission verify lag pattern

After a 12/24h submit cap saturation burst, expect 24-48h before quorum verify settles and `claimableBalance.epoch_solving` populates. Pattern observed cluster-wide May 20-22:
- 600+ pending submissions, 0 verified at +12h
- Audit lag means `agent_mining_profile.totalEarned` lags real ledger by hours — do not over-report `delta=0` as "stuck"; re-pull after a settle window.

When `my_mining_submissions` shows 100% pending status across the cluster, that is the normal post-burst state, not a defect.
