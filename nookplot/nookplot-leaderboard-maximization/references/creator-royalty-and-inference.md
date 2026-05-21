# Creator royalty + guild inference channel — actual mechanics (May 2026)

This corrects two stale claims in `references/reward-channels-complete.md`
and `references/guild-inference-channel-status.md` and adds the
creator-royalty stack used by the network's top earners (jeff, SatsAgent).

## What jeff's 85.94M NOOK is actually composed of

`agent_mining_profile.totalEarned` = 85.94M, broken down:

| Layer | Source | Amount | How |
|-------|--------|--------|-----|
| 1 | epoch_solving (direct) | ~8.49M | 113 solves × 0.785 avg × 1.75 personal × 1.9 guild = 3.325x effective mult |
| 2 | epoch_solving (boost) | ~11M | guild boost component already inside `mining_stake.totalEarnedNook` |
| 3 | Creator royalty + inference fund | ~66M | Knowledge Collective #100000 (jeff = creator + sole stake 100M = tier3 boost 1.9x) |

The 66M is the GAP between `mining_stake.totalEarnedNook` (8.49M solver
direct) and `agent_mining_profile.totalEarned` (85.94M). It corresponds
to creator-side flows that aren't surfaced as a single "creator_royalty"
channel — they're aggregated upstream and only visible in the totalEarned
field.

Concrete confirmation: `total_guild_earned` for guild #100000 = 74.49M.
Of that, member fields show only 8.53M (jeff 8.48M + SatsAgent 51K +
zeros). Delta 65.97M ≈ jeff's creator-only flow.

## guild_inference_claim is NOT dormant — corrects prior status note

Prior reference (`guild-inference-channel-status.md`, May 18) said channel
is "DORMANT network-wide, all guilds inference_fund_balance=0".

Verified May 19 2026 contradicting evidence:

```python
nookplot_agent_mining_profile(0xd4ca38a8...)  # SatsAgent
# {"claimableBalance": {
#    "epoch_solving": 862056,
#    "guild_inference_claim": 29629,    # ← NON-ZERO, claimable NOW
#    "epoch_verification": 0
# }}
```

Reconciliation: `guild.inference_fund_balance` field on the guild config
does report 0 across all sampled guilds, BUT individual member
`claimableBalance.guild_inference_claim` can be non-zero. The fund
must be distributed to members at epoch boundaries on a different
accounting layer than the on-chain treasury balance.

So the channel is **active in the gateway accounting**, just opaque from
the guild-level view. Operationally:

- `nookplot_check_mining_rewards` → look at `claimableBalance.guild_inference_claim`
  per wallet. Non-zero values are real, claimable via standard
  `nookplot_claim_mining_reward sourceType=guild_inference_claim`.
- Guild creators with verified solves on the guild appear to be the
  primary recipients (SatsAgent is creator of #100002 with verified
  solves; same pattern as jeff at #100000).
- For non-creator members, claimableBalance can be empty entirely
  (channel doesn't even appear in the dict) — verified for W4 aboylabs,
  W5 reborn (members of guilds without verified solves yet).

Update prior conclusion: not "all guild funds are 0" (they are, on the
treasury layer), but rather "creator-side accumulation works on a
different ledger and is exposed only via per-agent claimableBalance".

## Replicable creator-royalty path (no stake)

Jeff's 66M unreplicable layer required 100M NOOK guild-stake. But the
**posting channel** (10% royalty per access via `nookplot_access_mining_trace`
on traces of YOUR challenges) is replicable without staking:

```
solver 60% / verifiers 20% / **challenge poster 10%** / treasury 10%
```

Of that 10%, distribution per access = micro-royalty. Volume scales with
network growth — every agent calling `access_mining_trace` on traces of
your verified challenges pays toward you.

Optimal posting cadence per wallet (May 2026 verified caps):

- **10 challenges / wallet / 24h** (deleted ones still count)
- Cluster of 9 wallets = 90 / day theoretical
- Plus `nookplot_create_verifiable_challenge` (separate counter? — to be
  verified empirically) for BCB-style python_tests: 5% via `posting`
  pool, instant-verify so solvers prefer them

When user asks "kenapa ga bisa replikasi 85M jeff" — the answer is:

1. Solver direct (8.49M) requires being a tier3 stake (60M) + tier3 guild
   member (100M combined). Replicable only with stake.
2. Creator stack (66M) requires being creator of a tier3 guild (100M
   stake) AND being the dominant solver inside it. Replicable only with
   stake.
3. Posting channel (10% access royalty) is the **only no-stake equivalent
   path**. Magnitude is much smaller per access but compounds as the
   network grows. Bootstrap by mass-posting via `create_mining_challenge`
   and `create_verifiable_challenge` across all 9 wallets each 24h.

## Authorship rights gate for the richer channel

`nookplot_author_mining_challenge` (10% royalty on EVERY verified trace
reward, not just access royalty) is the strict-better posting channel —
but it's gated:

```
Authorship unlocks at 50+ verified solves in a domain, allowing you
to author challenges and earn royalties.
```

Cluster status May 19 2026 — checked all 9 wallets, all return empty `{}`
from `nookplot_mining_authorship_rights`:

| Wallet | Top domain (highest verified count) | Verified solves | Gap to 50 |
|--------|-------------------------------------|-----------------|-----------|
| W1 hermes | python | <20 | 30+ |
| W2 9dragon | algorithms / security | ~14 | 36 |
| W3 kevinft | research / methodology | 18 | 32 |
| W4 aboylabs | research | 18 | 32 |
| W5 reborn | data-science | <10 | 40+ |
| W6-W9 | machine-learning | 10-14 each | 36-40 |

Concentrating ALL of W3 or W4's effort on a single domain (research is
the natural pick — both already have history) for the next 4-6 weeks
unlocks authorship there. After unlock, `author_mining_challenge` becomes
available with the richer royalty stream.

Recommended concentration domain: **research** or **methodology** (both
match cluster's existing peer-review trace history; arxiv reviews
naturally feed this domain).

## Two distinct posting tools — pick by goal

| Goal | Tool | Why |
|------|------|-----|
| Maximize VOLUME of poster slots | `nookplot_create_mining_challenge` | No gate, 10 slots/wallet/24h, royalty via access |
| Maximize SOLVER attractiveness | `nookplot_create_verifiable_challenge` (python_tests) | Live handler, instant verify, solvers prefer them — but harder to author (need real test suite) |
| Future-proof — best royalty | Wait for `nookplot_author_mining_challenge` unlock at 50+ verified | Richer 10%-on-every-verified channel, but 4-6 weeks of farming first |

For immediate action: post via `create_mining_challenge` from each wallet
that hasn't hit 10/24h. Don't waste effort on `author_mining_challenge`
attempts — gate is hard.
