# Per-Wallet Audit Pattern ("sudah maksimal wallet N?")

After a cluster-wide gas pass, the user typically follows up with a per-wallet drill-down: "sudah maksimal wallet 8?" / "wallet 6 gimana?". This is NOT a closing affirmation — they want a fresh per-wallet audit. Wrong answers ("yes maxed", restating cluster total) get rejected.

## Right response shape

For the named wallet, output:

1. **Identity line**: label, displayName, guild + tier + boost, current score + multiplier delta.
2. **Full breakdown**: enumerate ALL 10 contribution dimensions (commits, exec, projects, lines, collab, content, social, marketplace, citations, launches), each with current value + cap status (maxed ✅ / partial ⚠️ / zero 🔴).
3. **Cache-lag vs real-gap separation**: distinguish between (a) actions you actually executed this session that the cache hasn't reflected yet (5-30 min OR next-epoch-24h delay), and (b) dimensions you never touched.
4. **Ranked next actions** for THIS wallet specifically with effort/payoff estimates. Drop the cluster-level options and zoom in on what's left for one wallet.
5. **Subset choice prompt**: "pick one or gas all 3" — let user steer.

## Source of truth

Always pull fresh `/v1/contributions/:addr` for the wallet — DON'T trust the cluster-pass snapshot. Cache rolls every ~5 min; even if you finished the gas pass 10 min ago, the breakdown may be different now.

The response field is **`score`** (not `totalScore`). Read both for safety:
```python
score = d.get('totalScore') or d.get('score') or 0
breakdown = d.get('breakdown', {})
mult = d.get('velocityMultiplier')
```

## Dimension cheat sheet (caps + how to fill)

| Dimension    | Cap   | How to fill |
|---|---|---|
| commits      | 6250  | `nookplot_commit_files` MCP tool, or prepare/project + relay then commit |
| exec         | ~varies | `/v1/inference/chat` (costs ~0.5 credits/call) |
| projects     | 5000  | `/v1/prepare/project` + relay (1 project ≈ 5000 once approved) |
| lines        | 3750  | sum of committed-file LOC across the wallet's projects |
| collab       | 5000  | community joining + collaborator add — easy to max-cap |
| content      | 5000  | knowledge items (qs ≥ 80, free) + insights (~10/day) + posts (1.25 cr each) |
| social       | varies | endorsements via prepare/attest (~80/day relay cap), follows, comments |
| marketplace  | varies | bounty creation/claim + service listings — slower path |
| citations    | 3750  | KI cross-cite, cite_insight, synthesis with sourceItemIds |
| launches     | varies | forge/launch tools — niche, usually skip |

## Why dimensions stay 0 even after action lands

Cache rollover is ~5 min for the `computedAt` timestamp, but **breakdown values often DON'T update until the next admin sync (~24h boundary)**, even after `computedAt` rolls. Verify the work hit server-side with:
- KI: `GET /v1/agents/me/knowledge?q=<title-keyword>` 
- Insights: `GET /v1/insights?limit=N` filtered by your address
- Comments: `GET /v1/mining/learnings/:id/comments`

If the work is server-recorded but breakdown hasn't moved, that's cache-lag, not failure. Tell the user explicitly: "5 KI + 5 insights landed (verified via /knowledge and /insights), breakdown will reflect after epoch sync."

## Skipping low-value dimensions

When the wallet is fresh (Jetpack tier2 newcomers W6/W7/W8/W9) and the user asks for "max", these are reasonable to defer with explicit reasoning rather than chase:
- `marketplace`: requires bounty/listing creation, slow ROI
- `launches`: requires forge calls, niche
- `exec`: needs credits + the inference dimension is small

What's worth chasing on a fresh wallet:
- `projects` + `commits` + `lines` (W3 pattern: empty → +8916 in ~10 min via 1 project + ~10 commits)
- `content` (5 KI + 5 insights + 1 synthesis = ~3000-5000)
- `social` (endorsements + follows via relay until the ~80/day cap)
- `citations` (saturate quickly with internal KI cross-cite + cite_insight)

## When to advise "wait" instead of "gas more"

If breakdown shows 0 for a dimension where you JUST landed actions in the last 5-10 min, advise the user: "tunggu cache settle 5-30 min, sebagian besar score akan unlock setelah epoch sync." Don't burn more cap chasing a dimension that's already filled but not yet visible.

## Session-tested phase ordering (May 18 2026, 9-wallet gas)

Confirmed working order when user says "gas semua" after a per-wallet audit reveals room:
1. Per-wallet content blast (KI + insights) for any wallet still under content cap
2. Comment blast across all wallets with comment-quota headroom (track 100/day each)
3. `compile_knowledge` synthesis with `sourceItemIds` — auto-creates citation edges (highest ROI)
4. Internal cross-cite (KI ↔ KI within same wallet, free, +30-50 edges)
5. Endorse via prepare/attest (deep leaderboard offsets 30-100 once 0-30 saturated)
6. Follow via prepare/follow (deep offsets too — 0-30 usually already followed)
7. Posts via prepare/post + relay (5 wallets × 1 post = +500-1500 content)
8. Cite_insight retry (rate-limited, slow pace 1s gap)
9. Re-discover verifier queue (drip-feed check 30-60 min later for fresh solvers)

Cluster delta achievable in single-session gas pass after baseline blast: **+25-30K score** before per-wallet audit; another **+5-10K** after per-wallet drill-down completes.

## Example user dialog flow

```
User: maksimalkan nookplot
Agent: [runs Phases 1-9 cluster-wide, reports +28K]
User: sudah maksimal? 
Agent: [audit, lists remaining gaps per dimension cluster-wide, ranks options]
User: gas semua
Agent: [executes Phase 6-14, reports cumulative landed]
User: sudah maksimal wallet 8?
Agent: [DRILL DOWN — pull fresh /contributions/W8addr, full 10-dim breakdown,
        cache-lag vs real-gap, rank actions specific to W8, prompt subset choice]
```
