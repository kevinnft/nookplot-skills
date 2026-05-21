# Mining Guild Economics & Domain Lock

The session that produced this note opened with the user pointing at a single
wallet's 1.5M lifetime NOOK and asking how to replicate it on a new wallet.
The answer was nuanced enough that future-self should not re-derive it from
scratch.

## Reward channels per wallet (from `nookplot_check_mining_rewards`)

`claimableBalance` dict shape tells you which channels a wallet has access to:

| Channel | Source | Magnitude |
|---|---|---|
| `epoch_solving` | Per-solve dilution from epoch 70% pool | 100s-1000s NOOK per solve |
| `epoch_verification` | 5% verification pool, distributed by share | 10s-100s NOOK |
| `guild_inference_claim` | **Where the big money lives** — guild fees from solved deep-dive challenges + 20% epoch guild pool | 10K-1M+ NOOK over weeks |
| `dataset_royalty` / `authorship` / `posting` | Niche | Small unless you authored a popular bundle |

A wallet's `claimableBalance` dict will simply NOT include `guild_inference_claim`
if it has never been in a tier1+ guild. That's the smoke that tells you which
wallets in the cluster have access to the big channel and which don't.

## The 1.5M misconception

Lifetime totals like W2's 1.27M are **2-month accumulations across many guild
solves and multiple epoch settlements**, NOT per-task rewards. Per-task math:

- Deep-dive challenge: `estimatedRewardNook ≈ 5,683` per solver slot, `maxSubmissions: 3`
- Even if a single guild grabs all 3 slots, the cap is ~17K NOOK per challenge
- Reaching 1M+ requires the guild claiming 50+ deep-dives over weeks AND the
  agent participating consistently with high comprehension/verification scores

## Domain-lock gate on guild claim (verified May 18 2026)

`POST /v1/mining/challenges/{id}/claim {"guildId": N}` returns:
```
{"error": "Guild is missing required domain specializations: methodology",
 "code": "MISSING_DOMAINS"}
```

The gate: the guild's `domain_specializations` set must be a SUPERSET of the
challenge's `requiredDomains`. The challenge field shows up in the
`/v1/mining/challenges/{id}` GET response — read it before joining a guild.

### Practical implication: not every tier1+ guild can claim every deep-dive

As of May 18 2026, the 6 deep-dive challenges in the open pool all required
`[research, methodology]`. Of 51 mining guilds, only TWO matched both AND were
tier1+:

| Guild | Tier | Slots | domains include | Status |
|---|---|---|---|---|
| The Lyceum Collective (id 5) | tier3 | 6/6 | arxiv_review, code-audit, methodology, peer-review, research | FULL |
| Neural Cartography (id 2) | tier3 | 6/6 | planning, coordination, multi-agent, creative-ai, python, typescript | FULL |
| Adversarial Analysis (id 4) | tier3 | 6/6 | cryptography, security, code-review, typescript, rust, debugging | FULL |
| Vector Field (id 7) | tier3 | 6/6 | data-science, ml, python, pytorch, nlp, rag, embeddings | FULL |
| Social Contract (id 9) | tier2 | 6/6 | methodology, research, ML, code-audit, data-quality | FULL |
| Jetpack (id 100045) | tier2 | 6/6 | code-review, ML, research, security | FULL, NO methodology |
| SatsAgent (id 100002) | tier1 | 2/6 (open) | algorithms, python | NO methodology |

**Full scan May 18 2026:** ALL tier2+ guilds are 6/6 FULL. No high-tier slots available.
Only SatsAgent (tier1, 1.35x) has open slots (4 available).

**Lesson:** when steering a fresh wallet into a tier2 guild for "big rewards",
verify the guild's `domain_specializations` against the actual deep-dive
`requiredDomains` distribution in the open pool. A tier2 boost is worthless
if the guild can't claim any of the high-reward challenges.

## When to set expectations vs jumping to action

User's "amankan wallet bersama wallet lainnya dan beri nama satoshi, fokus
join guild tier tinggi dan kerjakan task reward 1,5M nook itu" had three
sub-goals stacked:

1. Create + secure W6 (cluster mirror) — DOABLE, ~3 minutes
2. Join high-tier guild — DOABLE if tier2 has slots, did join Jetpack
3. "Earn 1.5M NOOK from that task" — UNREACHABLE on the current pool because
   Jetpack lacks methodology specialization AND deep-dive per-task cap is ~17K

**Right move (and what was done):** complete the safe, doable steps (1+2),
THEN deliver the reality check on (3) before burning more cycles. Do NOT
charge into challenge submission claiming you'll deliver 1.5M when the math
says max realistic is ~3.4K.

The user explicitly thanked the framing in past sessions ("cek ulang" =
honest gap analysis, not "we plateaued"). Stretch goals deserve transparent
limits, even when the user phrased it as a directive.

## Fallback options when domain-lock blocks the goal

A. **Stick in tier2 guild, submit to non-deep-dive challenges**
   - 1.6x boost on standard challenges still earns 1K-2K NOOK each
   - Wait for new deep-dives that match guild domains

B. **Move to a domain-matching tier1 guild**
   - SatsAgent tier1 1.35x is open if domain matches
   - Lower boost but actual deep-dive access if their domain list intersects

C. **Bikin guild baru** — requires NOOK stake, user has flagged "tidak mau
   stake" multiple times → off the table

D. **Wait for slot** in Knowledge Collective or Social Contract (both full)
   — passive, weeks-to-months timeline

The honest answer is usually A unless the user is willing to revisit C/D.

## Inference Fund Depletion (confirmed May 18 2026)

ALL known guilds (IDs 2-9, 100002, 100017, 100032, 100045) show
`inference_fund_balance: 0`. The `guild_inference_claim` reward channel is
effectively dead network-wide — no new NOOK is accumulating in any guild's
inference fund.

**Implication:** W4's 860K lifetime total from guild_inference_claim is a
historical artifact. It CANNOT be replicated by other wallets today. When the
user asks "bisa gak semua wallet dapet reward besar kayak W4?" the answer is
NO — the source is depleted. The only active reward channels now are:
- epoch_solving (per-solve, small)
- epoch_verification (5% pool, moderate)
- dataset_royalty / authorship / posting (niche, small)

Guild membership still matters for the BOOST MULTIPLIER on epoch rewards
(1.35x-1.9x), but the passive income channel (inference fund) is dry.
