# When user opens with "1.5M NOOK challenge" — calibrate first

User-facing quick-reference for the recurring pattern where someone reads the
nookplot.com Mining UI's "1.5M NOOK" line on a guild deep-dive and asks the
agent to "selesaikan semuanya" / "kerjakan semua untuk maksimalkan reward".

## The calibration that must come first

`baseReward: 1500000` from `GET /v1/mining/challenges/:cid` is the GUILD POOL
CEILING distributed across the entire guild over the challenge's verification
window (typically 144h), NOT per-submission.

Real per-submission expectation comes from `estimatedRewardNook` on the same
endpoint. Empirically across May 2026 deep-dive challenges:

| Field                  | Typical value      | Meaning                          |
|------------------------|--------------------|----------------------------------|
| `baseReward`           | 1,500,000          | guild-pool ceiling, 144h window  |
| `estimatedRewardNook`  | 4,000-6,000        | per-quality-submission realistic |
| Tier2 boost (1.6x)     | × 1.6              | applied if solver in tier2 guild |
| Composite score factor | × 0.5-1.0          | based on 4 verifier dims         |

So a tier2 wallet with composite ~0.7 lands ~5K NOOK per deep-dive submission,
NOT 1.5M. To realistically hit 1.5M total per challenge, every spot in the
3-submission max would need to land at composite ~1.0 with tier3 boost
(1.9x) — empirically unobserved.

## Cluster ceiling for an unstaked 9-wallet operator

Per epoch (24h rolling), GUILD_EXCLUSIVE slot is 1/wallet AND it's SHARED
with documentation_gap + citation_audit + sybil_audit submissions (see
`guild-exclusive-slot-shared.md`). Tier1+ eligible wallets for deep-dives
are typically 4-5 of the 9 in a mixed cluster.

```
realistic per-epoch ceiling = 4-5 deep-dive submissions × ~5K NOOK
                            ≈ 20K-30K NOOK / 24h from this lane
```

NOT 12M (8 challenges × 1.5M) which the UI math would suggest.

## How to communicate this to the user

When the user opens with "ada reward 1.5M, gas selesaikan semua":

1. State the calibration up front in 2-3 sentences. Don't bury it in a
   wall of mining mechanics.
2. Show the math: estimatedRewardNook × cluster eligible × tier boost.
3. Then describe the per-wallet slot state and what's executable NOW.

DON'T:
- Promise 1.5M-per-submission yields
- Open with eligibility mechanics before the calibration — user thinks
  the question is "which wallets can submit", but the more important
  question they didn't know to ask is "is the reward what I think it is"
- Bury the calibration in a footnote — they'll skim past it and feel
  cheated when the rewards settle at 6K instead of 1.5M

DO:
- Open: "Real per-submission ~5K NOOK, not 1.5M (UI shows pool ceiling).
  Cluster total ~25K if all 5 eligible wallets land good submissions."
- Then move to slot state, eligibility map, paraphrased trace prep.

## Why this calibration is durable

The 1.5M number is a UI-design quirk that will not change — it accurately
reflects the pool ceiling, just under a label users misread as
per-submission. Until the UI relabels it, every session where the user
asks about a deep-dive will start with the same misconception. The
agent's job is to defuse it within the first response, not after the
user has already mentally banked the win.
