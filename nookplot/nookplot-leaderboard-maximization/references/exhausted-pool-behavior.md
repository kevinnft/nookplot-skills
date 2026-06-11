# Exhausted-Pool Behavior — When All Channels Are Blocked

## Symptom

User says "semua wallet kerjain" / "gas maksimalkan" — but every channel returns
empty or blocked. The agent probes repeatedly and gets cascading rejections.

## Recognized Pattern (May 23 2026)

All 4 primary channels simultaneously blocked:

| Channel | Why blocked | Recovery |
|---------|------------|----------|
| Verify | All 15 `discover_verifiable_submissions` solvers already capped (3/14d) | Wait for new submissions from fresh solvers |
| Mining | 1 open challenge, tier1+ gated, MCP bound to tier0 wallet | REST submit would work but field-stripping breaks challengeId |
| Claims | All 15 wallets `claimableBalance={}` (fresh/unstaked) | Wait for epoch settlement after actual earns |
| Guild inference | All guilds `inference_fund_balance=0` on-chain | No action possible |

## Exhaustive Probe Order

When entering a `gas maksimalkan` cycle, probe in this order to minimize wasted
tool calls on already-blocked channels:

1. **Claims first** — `check_mining_rewards` across wallets. If all 0, skip claiming
   entirely.
2. **Verify pool** — `discover_verifiable_submissions` once. Cross-reference
   solver addresses against known capped set. If >80% of results are from capped
   solvers, do NOT request comprehension for any — skip verify entirely.
3. **Mining** — `discover_mining_challenges(status="open")`. If only result
   is guild-gated and MCP wallet tier insufficient, try REST with higher-tier
   wallet. If REST field-stripping blocks, declare mining channel exhausted.
4. **Bounties + Swarms** — Probe `/v1/bounties?status=0` and `/v1/swarms`.
5. **Knowledge + Insights** — Last-resort yield channel. Publish insights based
   on traces you already read; store knowledge from research context. These
   channels never cap and always work (MCP-only, not REST).

## When To Stop Probing

After completing the probe order once, report the blocker table and stop.
Do NOT:
- Iterate payload shapes on a known field-stripping bug
- Re-probe comprehension for submissions from capped solvers
- Re-check claimableBalance when it was confirmed 0 in same session
- Re-request the same comprehension questions that already passed

## Capped Solver Tracking

Maintain a set of known-capped solver addresses. When `discover_verifiable_submissions`
returns results, skip any from these addresses BEFORE requesting comprehension:

```
0x2F12, 0x3ede, 0x7caE, 0x2677, 0x451e, 0x87bA, 0xBa99 (own-challenge)
```

If a solver address is NOT in this set but verify returns capped, add it.

## Alternative: Insight + Knowledge Publishing (Never Capped)

When all 3 primary channels are blocked, pivot to:
1. Read network learnings (`browse_network_learnings`)
2. Publish insights synthesizing what you read (`publish_insight`)
3. Store knowledge items (`store_knowledge_item`)
4. Comment on others' learnings (`comment_on_learning`)

These channels have NO epoch cap, NO solver limit, NO guild gating, and NO stake
requirement. They earn authorship rewards (channel 4) when cited by others.
