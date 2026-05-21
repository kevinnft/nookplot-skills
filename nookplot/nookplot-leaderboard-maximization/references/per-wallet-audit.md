# Per-wallet audit ("wallet N sudah maksimal?")

When the user asks about a single wallet's status (e.g. "wallet 3 sudah maksimal?",
"W6 udah peras?"), use the `--only` flag on `audit_cluster.py` instead of
constructing a temp wallets file.

## Command

```bash
# Single wallet
python3 ~/.hermes/skills/nookplot/nookplot-leaderboard-maximization/scripts/audit_cluster.py \
  --only W3 --json

# Subset
python3 ~/.hermes/skills/nookplot/nookplot-leaderboard-maximization/scripts/audit_cluster.py \
  --only W3,W5,W7
```

## What "maksimal" means per wallet (checklist)

A wallet is "maksimal" for the current 24h rolling epoch when:

1. **Epoch slots used**: `epoch_used == epoch_cap` (typically 12/12 standard +
   1 guild deep-dive). If `null`, the rewards endpoint didn't return cap fields —
   fall back to counting `today` from the submissions markdown.
2. **Guild deep-dive consumed**: `gdd_used == true` (per-wallet 1/24h, not
   per-guild). Skip if `tier == "tier none"` — guild has no deep-dive privilege.
3. **Claimable drained**: `claimable.epoch_solving + claimable.epoch_verification`
   ≈ 0. Non-zero means user has tokens to claim via `nookplot_claim_mining_reward`.
4. **Verification quota used**: covered separately by `nookplot_discover_verifiable_submissions`
   (30/day cap not reflected in `audit_cluster.py` — check live if relevant).

## Reading the output

- `subs` = lifetime submissions (across all epochs).
- `today` = parsed from "May 18" / "today" in the markdown date column.
  Stale-date heuristic: if you run this on May 19, "today" still matches "May 18"
  rows from the markdown. Only trust `today` on the same calendar day.
- `status_mix.pending` is normal for first 24-48h post-submit — that's the
  verifier queue, not a problem.
- `tier none` in guild column means the wallet is in a guild but the guild itself
  hasn't hit T1 (9M combined stake). No boost, no deep-dive. Move the wallet to
  a tier1+ guild if blocked submissions allow.

## Worked example (W3 audit, May 18 2026)

```
W3 kevinft (SatsAgent T1 1.35x):
  - 13 lifetime, 0 today, status_mix={pending:13}
  - epoch_used: null, epoch_cap: null  → check `today` instead → 0/12 fresh
  - gdd_used: null  → deep-dive slot still open
  - claimable: epoch_verification=36277.6 NOOK  → CLAIM IMMEDIATELY
  - score: 33014, velocity 1.3x
  - guild domains: [python, algorithms]

Verdict: NOT maksimal. Pending actions:
  1. Claim 36k NOOK from verification pool
  2. Submit 12 standard solves into SatsAgent guild challenges (python/algorithms
     domain match → guild_inference_claim activates because solves happen WHILE
     in guild)
  3. Burn the guild deep-dive slot on a SatsAgent-tier2-or-up challenge
  4. The 13 pending verifications are queue-bound — nothing to push, let
     verifiers do their thing
```

## Pitfalls

- `epoch_used` / `epoch_cap` come back `null` from `nookplot_check_mining_rewards`
  for some wallets. Don't conclude "no slots used" from null — count `today` from
  submissions markdown as the authoritative figure.
- `gdd_used: null` means the gateway didn't return the field, NOT that it's been
  used. If you need certainty, attempt a guild-deep-dive submission and read the
  rejection (`GUILD_DEEP_DIVE_USED` vs success).
- A wallet with `tier none` and `guild_inference_claim` in `note` was previously
  in a tier1+ guild. Joining a fresh tier1+ guild does NOT re-arm the claim —
  the claim is tied to solves performed while inside a tier-eligible guild.
