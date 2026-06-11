# Guild Deep-Dive minGuildTier Gate — Individual Stake, NOT Combined

Validated May 22 2026 against challenge `aff5f9f9-fdc1-4d1f-b379-38244c279ce8`
("Guild deep-dive: The Overlooked Repetitive Lengthening Form...", 1.5M base).

## What was confirmed

The `minGuildTier: tier1` filter on guild deep-dive challenges checks the
**individual submitter's stake tier**, NOT the guild's combined-stake tier.

W11 (WhiteAgent):
- Member of guild #10 (boost 1.9x active on regular submissions)
- Individual stake: 0 NOOK → stakeTier: `none`
- Submit attempt with `guildId: 10` explicit returned:
  `"Your guild is none but this challenge requires tier1+. Increase your guild's combined stake to upgrade tier."`

The error message says "combined stake" but the actual check is on the
SUBMITTER'S OWN stake. Guild boost still applies to score multipliers, but
the gate itself is per-wallet.

## Implication for no-stake strategy

Under the user's no-stake rule (W2..W15 hold 0 NOOK individual stake):
- Guild deep-dive challenges (typically 1.5M-2M base × guild boost = 2.85M-3.8M
  potential) are **permanently locked** for these wallets
- Only W1 (or any individually-staked wallet) can claim them
- Joining a tier3 combined-stake guild does NOT unlock these for unstaked
  members

## Reward-table re-ordering for unstaked wallets

When stake=0, the practical reward priority list becomes:

1. Regular expert challenges (500K base × 1.9x guild boost = 950K) — HARD CAP 12/24h
2. Guild-exclusive challenge (1/24h, separate epoch counter)
3. On-chain knowledge publish via forwarder relay (see onchain-publish-via-relay.md)
4. Verify external solver subs (no-stake earning, 5%/epoch pool)
5. Follow / endorse / attest (small contribution credit, social score)

Guild deep-dives drop OFF the list entirely until individual stake is added.

## Bypass option (if user permits)

The minimum stake to unlock tier1 is 9M NOOK individually. Self-attest doesn't
help; needs actual on-chain stake into the staking contract. User's no-stake
preference (May 2026) blocks this.

## Self-check before drafting trace

Before writing a 7-8K-char trace for a guild deep-dive (~30 min effort),
check `/v1/agents/{addr}/stake` or `nookplot_check_mining_stake` first. If
`stakeTier === "none"`, abort and pivot to a regular challenge — submitting
the trace will hit the gate AFTER you've spent the effort.
