# Hidden reward safe-probe pattern (May 23 session)

Use when the user asks to find “hidden reward”, “celah reward”, “semua yang ada reward”, or asks whether Nookplot is really maxed after visible mining/verification/bounty lanes look dry.

## Principle

Treat hidden reward as legitimate under-documented surfaces, not exploits. Execute only safe/off-chain actions automatically:

- read-only reward/ledger probes
- `compile_knowledge`
- `store_knowledge_item`
- `add_knowledge_citation`
- substantive non-spam comments if clearly useful

Do NOT auto-claim, stake, create paid listings, sign on-chain actions, or brute-force admin-ish endpoints without explicit user approval and a positive, inspectable balance/state.

## Probe surface checklist

For each W1-W15 API key, probe these classes before reporting “maxed”:

1. Mining rewards
   - `check_mining_rewards`
   - split `claimableBalance` into `epoch_verification`, `epoch_solving`, `guild_inference_claim`
   - report claimable sums separately from historical `totalEarned`

2. Bounty pipeline
   - `my_bounties`
   - status counts by `pending`, `approved`, `shortlisted`, `claimed`, `submitted`, `completed`
   - only execute next step if status clearly requires it and action is safe/approved

3. Revenue/credits
   - `/v1/revenue/balance`
   - `/v1/revenue/history`
   - `/v1/credits/transactions`
   - IMPORTANT: credit transaction `balanceAfter` is not claimable revenue. Do not include it as an earning opportunity.

4. Marketplace/verdicts
   - `my_agreements`
   - `list_credit_agreements`
   - `get_verdict_summary`
   - `get_recent_verdicts`

5. Autoresearch / spot-check / attention surfaces
   - `list_pending_spot_checks`
   - `available_subtasks`
   - `browse_clarification_needs`
   - `get_attention_signals`
   - `list_intents`
   - `generate_recommendations`

6. KG compounding
   - `compile_knowledge`
   - if clusters are substantive, store a class-level synthesis and cite source items.
   - This is the safest action to execute while claim/bounty/verification are blocked.

## Interpretation rules

- Historical `totalEarned > 0` means the wallet has earned before; it does NOT mean claimable now.
- `claimableBalance` all zero means no claim should be attempted.
- Bounty applications all `pending` means no claim/submit path is open; report as pipeline value only.
- `totalVerdicts: 0` and empty spot-check trajectories means marketplace/spot-check lane is dry.
- Rate limit on a subset of wallets is a temporary read blocker; do not retry aggressively in the same turn. Mark the affected wallets and re-probe later.
- If a probe returns many positive numeric fields, filter by semantic path names. Counts, `balanceAfter`, limits, and historical totals are context, not actions.

## Reporting shape

For Nookplot maxed/hidden-reward reports, include:

- timestamp in UTC and WIB
- report path if a JSON report was written
- safe actions actually landed, with IDs and quality score if KG
- claimable sums by reward slot
- bounty status counts and top coverage IDs
- ranked opportunities
- blockers
- exact next action / re-poll interval

Avoid saying “all done” without naming the dry lanes. The user expects concise but complete technical status.
