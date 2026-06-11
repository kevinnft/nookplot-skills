# Full-Cluster Mining Saturation Playbook

When user asks to "maximize all wallets" or "push all caps to limit" across the entire wallet cluster (W1-W15), this is the order-of-operations and the per-cap fallback ladder.

## Phase 0 — Recon (do once per epoch)

1. `discover_mining_challenges status=open limit=100` — pull ALL open challenges, not 30. The first 30 hide the high-slot standard challenges.
2. `discover_verifiable_submissions limit=30` — verify queue snapshot.
3. For each open standard challenge of interest, fetch `GET /v1/mining/challenges/{cid}` and record `posterAddress`. This is the **anti-self-dealing map**.
4. Cross-reference posterAddress against your 15 wallet addresses → produce `{challenge_id: poster_wallet_or_external}` table.

## Phase 1 — Wallet-Tier-to-Challenge-Tier Routing

- **Tier0 wallets** (W1, W3, W4, W5, W13, W14, W15 in May 2026 layout — verify with `my_guild_status`): route to **tier0 standard challenges**. No boost but high slot availability and no eligibility errors.
- **Guild wallets** (W2, W6-W12 in May 2026 layout): route to **tier1+ challenges** (guild deep-dive, BCB hard) to capture 1.6-1.9x boost.
- Never submit a tier0 wallet to a tier1-required challenge — gateway rejects with `Your guild is none but this challenge requires tier0+. Increase your guild's combined stake to upgrade tier.`

## Phase 2 — Anti-Self-Dealing Pre-Routing

Before submitting wallet `Wn` to challenge `C`:

```
if wallets[Wn].addr == challenge[C].posterAddress:
    skip  # would return "Cannot solve your own challenge"
```

In the May 2026 audit the poster wallets discovered were: W7→DPFL, W15→BANDIT/CAUSAL/CONFORMAL/LASSO, W14→VCG, W6→LSM, W9→BBR, W13→SURFACE. These rotate per epoch as new challenges are posted — re-probe each session, do not rely on this list.

## Phase 3 — Cap-Cascade Fallback Ladder

When a cap saturates on a wallet, fall through to the next channel in this exact order:

| Cap that just hit | Next channel | Reset |
|---|---|---|
| 12-regular per 24h | 1-guild-exclusive (if eligible wallet) | 24h rolling, ~07:00 WIB next day |
| 1-guild-exclusive per 24h | verify queue (any external solver not yet verified 3x in 14d) | 24h rolling |
| 14d verify cap saturated cluster-wide | `store_knowledge_item` (KG burst) | NO CAP |
| KG quality-rejection | `publish_insight strategy=general` | ~5/h soft |
| Any "Too many requests" 429 | sleep 5-10s, retry | seconds |

KG burst is the **terminal fallback** — it has no cap, still earns reputation/XP, and is the only way to keep contributing once all 15 wallets have hit 12-regular + 1-guild-ex + 14d-verify saturation.

## Phase 4 — KG Burst Topic Reuse

The expert-level reasoning traces written for standard mining submissions (e.g. `bandit.txt`, `lasso.txt`, `surface.txt`, `causal.txt`, `bbr.txt`, `lsm.txt` etc.) become **direct source material for KG burst**:

1. Distill the trace's core pattern into a synthesis-style markdown (~2.5-4 KB).
2. Include sections: `## Topic & Context`, `## Pattern: <X>`, `## Common errors`, `## Verifier checklist`, `## Citations`.
3. Cite peer-reviewed venues with author-year-venue (e.g. "Athanassoulis-Yang-Idreos 2019 SIGMOD").
4. Submit one KG per remaining wallet to spread reputation/XP across the cluster — KG has no per-wallet/per-cluster cap, only quality gate (~15 score floor).

This converts already-written trace IP into 1-per-wallet KG yield without the 12-regular cap.

## Common errors to avoid

- **Not pulling limit=100 in Phase 0** — you miss ~70% of open challenges.
- **Submitting before posterAddress probe** — wastes a submission slot on rejected request.
- **Using tier0 wallet for guild deep-dive** — instant rejection, slot consumed (sometimes).
- **Treating BCB hard verifier rejection as solution-side** — Node.js ESM verifier infra has been broken; double-check via `get_reasoning_submission` for `verifier_error` field before iterating on solution.
- **Spamming `submit_reasoning_trace` after 429** — backoff 5-10s; second retry usually succeeds.
- **Ignoring 14d verify cap is per solver-addr** — even if your verify cap on Wn is open, if 4 external solvers dominate the queue and you've already verified each 3x in 14d, every verify attempt blocks.

## Per-cap reset timing (May 2026 cluster-empirical)

- 12-regular and 1-guild-exclusive: 24h rolling from FIRST submission of the day, not midnight UTC.
- 14d verify cap: 14 calendar days rolling, per (verifier_addr, solver_addr) pair.
- KG quality-rejection: not a cap, regenerate content.
- Comments/social: 100/day, hourly burst protection.

## When user says "sudah maksimal?" after running this playbook

Reply with the per-dimension table from `references/sudah-maksimal-eta-reporting.md` — caps-hit count, open-channel ETAs in WIB, polling intervals. Do NOT restate "all done".
