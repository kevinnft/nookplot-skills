# Guild-Exclusive Mining: Shares Epoch Cap (May 25, 2026)

## Critical Finding
Guild-exclusive challenges (`discover_mining_challenges` with `guildOnly: true`) **share the same 12/12 regular epoch cap** — they are NOT a separate slot.

## Evidence
- W3 (guild 100002, tier3, boost 1.9) at 12/12 regular cap → guild-exclusive submit returns `EPOCH_CAP`
- Confirmed across multiple wallets (W3, W6, W7) — all blocked

## Implication
- Guild-exclusive is a **challenge filter**, not an additional daily allowance
- The "1 guild-exclusive per day" mentioned in docs may refer to a different mechanism (guild-wide cap, not per-wallet)
- When all wallets are at 12/12 regular cap, guild-exclusive is also blocked

## Previous Assumption (WRONG)
Earlier sessions assumed guild-exclusive = separate 1/day slot on top of 12/12. This is incorrect.

## Strategy Update
- Mine guild-exclusive challenges **early in the epoch** (counts against 12/12 but gets guild boost)
- Do NOT defer guild-exclusive to after regular cap is hit
- Tier3 wallets (1.9x boost) should prioritize guild-exclusive challenges when available
