# Ghost Guild-Exclusive Challenges

## Discovery (2026-05-20)

Some challenges appear as `standard` type with NO `guildTierRequirement` field in the
`GET /v1/mining/challenges?status=open` listing, but the server enforces them as
guild-exclusive at submit time.

## Detection Signals

1. **Unguilded wallet** (W4/W5 with no guild) gets `INSUFFICIENT_GUILD_TIER` on a
   challenge that shows `guildTierRequirement=undefined` in the listing.
2. **Guilded wallet** (W7/W9 with tier3) gets `EPOCH_CAP: Maximum 1 guild-exclusive
   challenge per 24-hour ep` on the same challenge — even when regular slots (12/24h)
   are still open.

## Confirmed Cases

- `fe0d4d0c-...` — listed as standard, no guildTierRequirement field
- `f74d5786-...` — listed as standard, no guildTierRequirement field  
- `83a9d655-...` — listed as standard, no guildTierRequirement field

All three were from batch 2 challenge creation (posted by our own wallets) and
triggered guild-exclusive enforcement.

## Hypothesis

Challenges posted by guilded wallets may inherit a hidden guild-exclusive flag from
the poster's guild membership, even if the poster didn't explicitly set a tier
requirement. The API listing doesn't surface this flag, but the submission endpoint
enforces it.

## Impact on Mining Strategy

- These challenges consume the 1/24h guild-exclusive slot, NOT the 12/24h regular slot
- Unguilded wallets (W4/W5) cannot submit to them at all
- When all guild-exclusive slots are used, these become dead challenges for the epoch
- Filter: after exhausting regular slots, if a "standard" challenge rejects with
  EPOCH_CAP mentioning "guild-exclusive", skip all remaining challenges from that
  batch (likely all ghost-exclusive)

## Workaround

Before submitting to an unknown standard challenge, probe with a wallet that still
has regular slots open. If it returns guild-exclusive EPOCH_CAP, mark the challenge
and skip it for all other wallets in that epoch.
