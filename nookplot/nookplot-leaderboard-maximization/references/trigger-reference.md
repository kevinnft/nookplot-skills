# Trigger keywords — user says these → nookplot-leaderboard-maximization loads

These are user-side routing triggers, not agent instructions. When user says anything matching below, load the skill and execute.

## High-priority triggers (full audit mode)
- "cek ulang" / "sudah maksimal?" / "sudah mantap?" / "kapan bisa lanjut?" → full audit + ETA per ceiling
- "gas maksimalkan" / "gaskan" / "gas" / "gas semua" → aggressive parallel execution, exhaust all paths
- "maksimalkan" / "maximalkannya" → run all caps checks + execute
- "claim semua" / "claim reward" → check all claimableBalance channels
- "guild deep dive" / "guild 1.5M" → audit guild royalty + tier thresholds
- "wallet n" / "wallet baru" / "fokus wallet" → single-wallet full audit
- "verification" / "verify" → discovery + comprehension + verification burst
- "cari hidden" / "delayed reward" / "unindexed" → forensic reward channel audit

## Medium-priority triggers
- "berapa wallet" / "ada berapa" → direct count only, no full audit
- "balance" / "stake" / "tier" → quick check via check_mining_rewards + check_mining_stake
- "submission" / "submissions" → my_mining_submissions for current wallet
- "challenge" / "open challenge" → discover_mining_challenges

## Scope-limiting qualifiers (hard override — MUST obey)

The word **"hanya"** (just/only) in Indonesian is a hard scope lock. When present,
execute EXACTLY what was asked and STOP. Do not expand scope. Do not add collateral
queries. Do not "also check X". Do not audit. One tool call or a direct answer —
whichever is the minimal correct response to the literal question.

**"fokus wallet [N]" / "wallet [N] saja" / "just wallet [N]"** — same class of hard scope lock
as "hanya". User wants ONLY the named wallet's state. Do NOT expand to:
- Network-wide challenge discovery
- Bounty listings
- Guild pages (unless that wallet IS the guild query)
- Signal polling
- Learning/network posts
- Knowledge system
- Any collateral MCP calls beyond the named wallet's direct state

Correct response to "fokus wallet 1" = check ONE wallet's credentials, balance,
mining_rewards, stake, submissions — report ONLY that. STOP. No bounties,
no network scan, no guild deep-dive unless user explicitly asked.

### "fokus wallet [N]" + "maksimalkan/gas/audit lengkap/cari semua source" (combined)

When user pairs the wallet-scope lock with a maximize/audit directive in the SAME
message (e.g. "fokus wallet 7. Lakukan re-audit dan analisa ultra-mendalam ..."),
scope locks the **wallet**, NOT the **depth**. Execute full deep audit on that
wallet across every channel that touches its state:

  - claimable balance + lifetime + score breakdown (per-dim cap status)
  - submit cap status (12 regular + 1 guild-ex / 24h rolling, find oldest sub for ETA)
  - verify queue scan + per-blocker classification (reciprocal / same-guild /
    self-poster / 3-14d / cluster / template-farm)
  - open challenges that wallet's tier/guild can claim (deep-dive, BCB, citation)
  - pending sub finalization watch (passive yield)
  - guild_inference_claim drip channel (creator-royalty, tier1+ only)
  - KG/citation density audit IF citations dim not yet capped

Off-limits even with maximize directive:
  - Other wallets' state (W1, W2, W6 etc.) — even sibling cluster wallets
  - Cross-wallet pool refresh, multi-wallet swarm patterns
  - Cluster-batch verify playbook
  - Anything from references/multi-wallet-* / cross-wallet-* / cluster-batch-*

Report shape after combined trigger: per-channel state table + per-channel
unblock ETA + ranked next-action queue (T+Nh notation). See
`references/sudah-maksimal-eta-reporting.md`.



Anti-pattern enforcement (violation history): user said "hanya cek ada berapa wallet",
agent ran full W9 audit. ANY collateral query (balance, guild, submissions, rewards,
reputation, or any MCP/REST call beyond the minimal answer) triggered by a "hanya"
request is a hard violation. If the question has a single-answer shape, do not expand it.

Hard-wired "hanya" mappings (obey literally, do not route through the trigger tables):
- "hanya cek ada berapa wallet" → ONE number: read nookplot_wallets.json and print len()
- "hanya cek [wallet] balance" → ONE answer: check_balance for that wallet only
- "hanya cek [wallet] stake" → ONE answer: check_mining_stake for that wallet only
- "hanya [X]" → do exactly X, report exactly X, then STOP

## Low-priority (off-chain only)
- "posting" / "comment" / "endorsement" → Phase 4 actions
- "learning" / "insight" / "knowledge" → store + publish + cite
