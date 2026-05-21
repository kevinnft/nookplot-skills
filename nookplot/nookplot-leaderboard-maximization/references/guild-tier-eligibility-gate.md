# Mining-tier eligibility gate (verified May 19 2026)

Cluster's current mining-guild assignments leave **all wallets locked out of
tier1+ deep-dive challenges**. Confirmed via empirical submit: error code
`Your guild is none but this challenge requires tier1+. Increase your guild's
combined stake to upgrade tier.`

## How to detect BEFORE submitting

When `nookplot_discover_mining_challenges status=open` returns rows tagged
🏰tier1 / 🏰tier2 / 🏰tier3, cross-check via:

```python
mcp_nookplot_nookplot_my_guild_status()
# Returns: {miningTier: 'none' | 'tier1' | 'tier2' | 'tier3', guildBoost: ...}
```

If `miningTier == 'none'`, ALL guild-restricted challenges are blocked
regardless of guild membership. The guild ID is irrelevant — what matters
is the combined-stake-driven tier on that specific guild.

## Gate vs cluster state (May 19 2026 snapshot)

Cluster mining guilds and tiers (from prior sessions + live verification):

| Wallet | Guild ID | Guild name              | miningTier |
|--------|----------|-------------------------|------------|
| W1     | 100017   | The Lyceum Collective   | none       |
| W4     | 100017   | The Lyceum Collective   | none       |
| W2     | 9        | Social Contract         | varies     |
| W3     | 100002   | SatsAgent               | varies     |
| W5     | 100032   | Quill Edge              | varies     |
| W6-W9  | 100045   | Jetpack                 | varies     |
| W10    | (joined) | Knowledge Collective    | tier2 1.6x (joined session) |

Per user rule (memory): **never `leave_guild` or `migrate_guild`** on cluster
wallets. The roster is fixed; we cannot bump Lyceum-100017 from `none`
without staking NOOK at the guild treasury, which the cluster has not done.

## Implication for "gas maksimalkan" runs

When the open queue is dominated by tier1+ deep-dive challenges (as it was
on May 19 2026 — 4/4 open challenges all tier1):

- Don't waste a slot probing tier-eligibility. The error message is
  unambiguous and the slot is consumed regardless of accept/reject.
- Pivot to `status=active` discovery — that filter surfaces 100+ standard
  + verifiable_code challenges that DON'T have tier restrictions. The skill
  body's main directive is "open queue empty → check active queue", which
  is even more important when the open queue is fake-full of tier-locked
  rows.
- Mention the gate to the user in the gas-maksimalkan summary so they
  understand WHY the deep-dive slot wasn't used. Don't let it look like
  the agent forgot.

## To unlock tier1 (informational, not currently actionable)

The combined-stake threshold for guild tier upgrades scales with the guild's
member roster. Lyceum-100017 has 2 members (W1+W4); to upgrade to tier1 the
guild's COMBINED stake needs to clear the threshold. Cluster has 0 NOOK
staked across all wallets per the user-no-stake rule, so this is structurally
blocked unless the user explicitly authorizes staking.

The other path — joining a tier1+ guild that already has the stake — is
ALSO blocked: cluster wallets are 1-of-1-guild and migration is forbidden.

So: tier1 deep-dive challenges are permanently out-of-reach for the cluster
under current rules. Skip them in queue discovery, focus on standard +
verifiable_code only.
