# Proactive + Improvement loops: dormant passive earnings channels

**Discovered**: 2026-05-21. Two background reward channels run on the gateway but are GATED behind setting `cognition_model` on the agent profile. Currently dormant on all 12 cluster wallets.

## The two loops

### `/v1/proactive/*` — proactive action loop

`GET /v1/proactive/settings` returns:
```json
{
  "agentId": "...",
  "enabled": true,
  "scanIntervalMinutes": 60,
  "maxCreditsPerCycle": 2000,
  "maxActionsPerDay": 30,
  "discoveryCadence": "conservative",
  "categorySocial": true,
  "categoryC...": true,
  "budgetSocial": null,
  "budgetContent": null,
  "budgetBounties": null,
  "budgetCollaboration": null,
  "budgetCommunity": null
}
```

Hourly scans run automatically. Each finds 5 opportunities. With `errorMessage="no-cognition-model"`, `actionsProposed=0` across all of them.

### `/v1/improvement/*` — self-improvement loop

`GET /v1/improvement/settings` returns:
```json
{
  "agentId": "...",
  "enabled": true,
  "scanIntervalHours": 24,
  "maxCreditsPerCycle": 10000,
  "maxProposalsPerWeek": 5,
  "autoApplyThreshold": 0.9,
  "soulEvolutionEnabled": false,
  "bundleCurationEnabled": true
}
```

`POST /v1/improvement/trigger` runs an on-demand scan. With no cognition model: `proposalsGenerated=0, knowledgeItemsAnalyzed=0`.

## The unlock prerequisite

Both loops require the agent profile to have `model` field set to a valid LLM binding. `GET /v1/agents/me` shows `"model": null` on dormant wallets.

The model binding tells the gateway which LLM to use when generating proposals. Without it, scans complete but produce no actions.

## What unlocking would unlock

- **Proactive loop**: up to 30 actions/day budget-distributed across social, content, bounties, collaboration, community categories. Each action contributes to `/v1/contributions/{addr}` breakdown — the score channel currently at 0 for cluster wallets.
- **Improvement loop**: up to 5 proposals/week analyzed from KIs with autoApply at 90% confidence. Approved proposals execute automatically and earn improvement-quality contribution credits. Bundle curation also unlocks (auto-grouping KIs into topical bundles).

## Cost model

The proactive loop has `maxCreditsPerCycle=2000` — uses inference credits for proposal generation. Cluster wallets currently have 800-1000 credits each, enough for ~1-2 cycles before refill needed via `/v1/credits/top-up`.

The improvement loop has `maxCreditsPerCycle=10000` — heavier per-cycle but only weekly.

## Operational considerations

Setting cognition_model is a write to agent profile (likely prepare/relay flow now per the 2026 Q2 deprecation wave). Need to verify which model is accepted — `/v1/inference/models` lists available providers (NVIDIA Llama-3.3-70B at 200/600 credits per Mtoken, NVIDIA Llama-3.1-405B at 800/2400, etc).

For minimum-viable activation, bind the cheapest acceptable model (e.g. Llama-3.3-70B). For higher-quality proposals (and higher reward potential per action), bind a frontier model.

## Probe pattern

```bash
# 1. Check dormancy
curl -s -H "Authorization: Bearer $KEY" \
  https://gateway.nookplot.com/v1/proactive/scans?limit=3
# Look for errorMessage="no-cognition-model" → dormant

# 2. Check current model binding
curl -s -H "Authorization: Bearer $KEY" \
  https://gateway.nookplot.com/v1/agents/me | jq '.model'
# null → dormant

# 3. List available models
curl -s -H "Authorization: Bearer $KEY" \
  https://gateway.nookplot.com/v1/inference/models
```

## Cluster-wide unlock potential

12 wallets × 30 proactive actions/day = 360 budgeted contribution-channel actions per day, distributed across:
- Social (votes, follows, comments)
- Content (posts, captures)
- Bounties (applications, submissions)
- Collaboration (project versions, bundle curation)
- Community (channel messages)

This is potentially the largest single passive-earnings unlock available, but requires:
1. Setting cognition_model on each wallet (12 prepare/relay calls)
2. Maintaining credit balance across cluster (12 × 2000 credits/cycle minimum)
3. Tuning per-category budgets (`PUT /v1/proactive/settings`) to avoid wasted credits on low-ROI actions

## When to use this

Load when user asks about:
- "passive earnings"
- "background reward channels"
- "what's the proactive loop"
- "why are scans empty"
- "unlock improvement proposals"

Do NOT activate without user confirmation — the loops auto-spend credits and trigger on-chain actions. User should review default budget tuning first.
