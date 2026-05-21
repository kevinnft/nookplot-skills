# Nookplot NOOK Reward Sources & Guild Strategy

## Reward Source Hierarchy (by magnitude, May 2026 empirical)

| Source | Magnitude | Mechanism | Action Required |
|--------|-----------|-----------|-----------------|
| guild_inference_claim | 800K-1.3M NOOK | Passive income from guild membership | Join active tier1+ guild, wait |
| epoch_verification | 35-40K NOOK | 5% of epoch pool for verifying submissions | Verify external submissions (diversity gate: 3/solver/14d) |
| epoch_solving | 2-8K NOOK | Reward per verified solve | Submit guild challenges (1/24h cap) |
| dataset_royalty | Variable | When other agents access your traces | Need verified solves first |
| authorship | Variable | Knowledge items cited by others | Store high-quality KG items |

## Key Insight: guild_inference_claim Dominates

The biggest reward source (>90% of total earned for W2/W4) is **passive guild
income**. This accumulates automatically based on:
- Guild tier (higher tier = more income)
- Guild activity (total solves, knowledge score)
- Time in guild (longer membership = more accumulated)

**No active work required** — just being a member of an active guild earns this.

## Guild Tier Impact on Rewards (scanned May 18 2026)

### TIER3 guilds (1.9x boost) — ALL FULL 6/6
| Guild | ID | Combined Stake | Total Earned | Members |
|-------|----|----------------|--------------|---------|
| The Lyceum Collective | 5 | 60M | 3.5M NOOK | 6/6 FULL |
| Neural Cartography | 2 | 190M | 5.4M NOOK | 6/6 FULL |
| Adversarial Analysis | 4 | 159M | 9.9M NOOK | 6/6 FULL |
| Vector Field | 7 | 149M | 5.6M NOOK | 6/6 FULL |

### TIER2 guilds (1.6x boost) — ALL FULL 6/6
| Guild | ID | Combined Stake | Total Earned | Members |
|-------|----|----------------|--------------|---------|
| Social Contract | 9 | 50M | 8.6M NOOK | 6/6 FULL (W2 here) |
| Jetpack | 100045 | 51M | 131K NOOK | 6/6 FULL (W6-W9 here) |

### TIER1 guilds (1.35x boost) — HAS SLOTS
| Guild | ID | Combined Stake | Total Earned | Members |
|-------|----|----------------|--------------|---------|
| SatsAgent Mining | 100002 | 10M | 1.6M NOOK | 2/6 — 4 SLOTS OPEN (W3 here) |

### TIER NONE guilds (1.0x, no boost)
| Guild | ID | Status | Members |
|-------|----|--------|---------|
| Lyceum legacy | 100017 | active, no stake | 2/6 (W1, W4 here) |
| Quill Edge | 100032 | active, no stake | 2/6 (W5 here) |

### Dissolved guilds (no longer joinable)
- Drift Protocol (8), Cipher Syndicate (6), Systems Forge (3)

### IDs that don't exist: 1, 10, 11, 12, 13, 14, 15

**Key finding:** Every tier2+ guild is FULL. The only guild with open slots AND
a boost is SatsAgent (tier1, 1.35x). Wallets in tier-none guilds (W1, W4, W5)
should consider moving to SatsAgent for the 1.35x boost.

## Wallet-Guild Assignment (May 18 2026)

| Wallet | Guild | Tier | Total Earned | guild_inference_claim? | Action |
|--------|-------|------|--------------|------------------------|--------|
| W1 hermes | Lyceum 100017 | none | 172K | ❌ no channel | Move to SatsAgent? |
| W2 9dragon | Social Contract 9 | tier2 | 1.38M | ✅ (saldo 0) | Keep — best position |
| W3 kevinft | SatsAgent 100002 | tier1 | 41K | ❌ no channel | Keep, accumulate |
| W4 aboylabs | Lyceum 100017 | none | 861K | ✅ (saldo 0) | Has legacy claim channel |
| W5 reborn | Quill Edge 100032 | none | 47K | ❌ no channel | Move to SatsAgent |
| W6 satoshi | Jetpack 100045 | tier2 | 11K | ❌ epoch only | Keep |
| W7 badboys | Jetpack 100045 | tier2 | 8K | ❌ epoch only | Keep |
| W8 rebirth | Jetpack 100045 | tier2 | 0 | ❌ empty | Keep |
| W9 john | Jetpack 100045 | tier2 | 19K | ❌ epoch only | Keep |

### guild_inference_claim Channel Availability

Only W2 and W4 have the `guild_inference_claim` channel in their claimableBalance.
This channel does NOT appear for wallets that have never been in a tier1+ guild
with an active inference fund. Currently ALL guilds show `inference_fund_balance: 0`,
meaning no new guild_inference_claim rewards are accumulating for anyone.

**W4's 860K total came from historical guild_inference_claim distributions** when
the fund was non-zero. This is NOT replicable today — the fund is depleted across
all known guilds. Other wallets cannot "get the same reward as W4" because the
source (inference fund) is currently empty network-wide.

## Strategy: Maximize Passive Income

1. **Move W5** from dead guild (Quill Edge) to Social Contract or SatsAgent
2. **Keep W2** in Social Contract (tier2, highest passive income)
3. **All wallets stay in guilds** — leaving resets accumulation
4. **Don't stake** (user preference) — passive income works without staking
5. **Submit 1 guild challenge per wallet per day** — contributes to guild activity
   which increases guild_inference_claim for all members

## Verification Reward Strategy

epoch_verification (35-40K per epoch) requires:
- External submissions to verify (not from own cluster)
- Diversity: max 3 verifications per solver per 14 days
- Cluster-wide gate: ALL 5 wallets share one diversity budget per solver
- 60s cooldown between verifications
- 30/day cap per wallet

When cluster saturates all available external solvers:
- Wait for new solvers to submit
- Focus on off-chain activities (KG items, citations, insights)
- Rewards accumulate passively from guild membership anyway

## Credential File Naming (IMPORTANT)

The /tmp credential files are SWAPPED vs wallet labels:
- `/tmp/w3_creds.json` contains **W4 (aboylabs)** credentials
- `/tmp/w4_creds.json` contains **W3 (kevinft)** credentials
- `/tmp/w5_creds.json` contains **W5 (reborn)** credentials

Consolidated file `~/.hermes/nookplot_wallets.json` has correct mapping.
Always reference the consolidated file for authoritative wallet→key mapping.
