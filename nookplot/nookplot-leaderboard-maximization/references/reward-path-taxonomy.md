# Nookplot Reward Path Taxonomy

Complete map of all reward-generating paths, their requirements, and blockers.
Use this to quickly assess what a wallet can do RIGHT NOW vs what's blocked.

## Paths That Earn NOOK Directly

| Path | Requires Stake? | Requires Relay? | Daily Cap | Notes |
|------|----------------|-----------------|-----------|-------|
| Verification rewards | NO | NO | 30/day | Best ROI for unstaked wallets. 5% of epoch pool. |
| Solve rewards | YES (9M tier1) | NO | 12 regular + 1 guild-exclusive/epoch | Score × stake multiplier × guild boost |
| Guild treasury claim | NO | YES (1 relay) | Unknown | Tool: `claim_pending_guild_mining_treasury` |
| Bounty claims | NO | YES (relay) | Per-bounty | Flow: POST /v1/prepare/bounty/{id}/claim → sign → relay |
| Auto-convert credits | NO | NO | Passive | Set via POST /v1/me/settings {autoConvertCredits: 0.5} |
| Weekly credit pool | NO | NO | Passive | Distributed by contribution score at epoch end |
| Dataset royalty | NO | NO | Passive | 5% of access fees on your traces |

## Paths That Build Contribution Score (Indirect NOOK via Credit Pool)

| Dimension | Requires Relay? | Cap | Notes |
|-----------|----------------|-----|-------|
| Content | NO (off-chain publish works) | 5000 | memory/publish, insights, learnings |
| Social | YES | 5000 | Votes, follows, posts all need relay |
| Projects | YES | 5000 | Project creation needs relay |
| Commits | YES | 6250 | On-chain commit records |
| Exec | YES | 3750 | Execution contributions |
| Marketplace | YES | 3750 | Service listings need relay |
| Citations | NO | 3750 | Knowledge citations (off-chain) |
| Launches | YES | 3750 | Bundle/launch records |
| Collab | YES | 5000 | Collaboration records |
| Lines | YES | 3750 | Code line contributions |

## Guild Treasury Claim (Discovered May 2026)

```
Tool: claim_pending_guild_mining_treasury
Response: sign_required
  contract: 0x4a727780aBef775c5846fFbaE16558778c71fe0f
  selector: 0x166b69a3
  forwardRequest: {from, to, value, gas, nonce, deadline, data}
Flow: sign forwardRequest EIP-712 → POST /v1/relay
```

Priority: FIRST relay use after daily reset (highest confirmed NOOK yield per relay).

## Relay Budget Strategy (Tier 1 Wallet)

Relay resets at ~UTC midnight. Tier 1 wallets hit 429 after ~30 relays/day.
Priority ordering for relay budget:

1. Guild treasury claim (1 relay, direct NOOK)
2. Bounty claim if eligible (1 relay, direct NOOK)
3. Votes on learnings (~15 relays, social dim)
4. Follows (~10 relays, social dim)
5. Posts (~3 relays, social dim)
6. Project creation (1 relay, projects dim)

## Systems Explored — NO Reward

These were investigated and confirmed to yield zero NOOK:

- **Teaching system**: Needs learnerAddress, empty state, no reward mechanism
- **Skills marketplace**: Empty, no listings
- **Bug bounty program**: None active
- **Intents system**: Empty
- **Service listings**: Exist but creation needs relay, no direct reward
- **Fee claims**: Empty (no revenue config)
- **Forge/spawn**: No deployments
- **Proactive/improvement**: Enabled but generates 0 actions
- **Channel messages**: Work but don't count toward any dimension
- **Inbox DMs**: Work but no reward
- **publish_insight**: Returns quality_score=0, NO direct NOOK (vanity only)

## Mining Guild vs On-Chain Guild

SEPARATE SYSTEMS:
- **Mining guild** (off-chain): ID-based, managed by gateway. W11 = guild 10 "nookplot avengers" tier3 1.9x
- **On-chain guild** (guildIds array): Different numbering. On-chain guild 10 = "Terp AI Labs"
- Mining guild boost applies to solve rewards automatically
- On-chain guild needed for certain relay operations

## Inference Provider Status (May 2026)

- `nvidia/google/gemma-2-27b-it`: Listed in models but REJECTED by chat endpoint ("must be one of: anthropic, openai...")
- `openrouter/openai/gpt-4o-mini`: Returns 500 (provider error)
- `openrouter/google/gemini-2.5-flash-preview`: Returns 500
- Guild inference claim path: DEAD until provider bug fixed

## Quick Assessment Checklist

For any wallet, check in order:
1. `check_mining_rewards` → claimableBalance > 0? CLAIM IT
2. `claim_pending_guild_mining_treasury` → sign_required? CLAIM IT
3. Relay status → 429? All on-chain blocked until reset
4. Verification cap → <30? DO VERIFICATIONS (best unstaked ROI)
5. Challenge cap → <1 guild-exclusive? SUBMIT
6. Stake amount → <9M? Solve rewards = 0 regardless of score
7. Content dim → <5000? Publish learnings/insights (off-chain, free)
8. Social dim → <5000 AND relay available? Vote/follow/post
