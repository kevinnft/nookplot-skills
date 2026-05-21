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
execute EXACTLY what was asked and STOP. Do not expand scope.

- "hanya cek ada berapa wallet" → output ONE number, no audit, no collateral queries
- "hanya [X]" → do exactly X, report exactly X

ANY other triggers combined with "hanya" still route by the tables above, but
output shape is constrained to exactly what was asked.

> Anti-pattern this session: user said "hanya cek ada berapa wallet", agent ran
> full W11 audit (balance + stake + guild + submissions + MCP queries). The agent
> violated the explicit scope lock and delivered 10× more than asked.

## Low-priority (off-chain only)
- "posting" / "comment" / "endorsement" → Phase 4 actions
- "learning" / "insight" / "knowledge" → store + publish + cite