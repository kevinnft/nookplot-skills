# Guild-Exclusive Slot is SHARED Across Sub-Types (May 19 2026)

## Discovery

User opened session asking to complete 2 guild deep-dive challenges (LLMLOOP +
UVM² RTL Verification) — both showed "1.5M NOOK" in UI, both `multi_step` /
`guild_cross_synthesis` / `tier1+`. Probe across the 5 eligible wallets
(W2 SocialContract9 t2, W6/W7/W8/W9 Jetpack t2) returned `429 EPOCH_CAP` on
every wallet despite only W6/W7/W8/W9 having known-recent guild deep-dive
submissions. W2 reported as having a free deep-dive slot in initial probe
(checked top 5 sub IDs only).

Full 24h-rolling audit (top 10+ subs per wallet, fetched all challenge meta)
showed W2's slot was consumed at 2026-05-18T21:39:44 UTC on a `Doc gaps:
docker/compose` submission — `sourceType: documentation_gap`, `challengeType:
standard`, NOT a guild deep-dive. Yet that submission DID consume W2's
guild-exclusive slot.

## Confirmed semantics

The `EPOCH_CAP` counter "Maximum 1 guild-exclusive challenge per 24-hour epoch"
covers ALL of these `sourceType` values via a single shared per-wallet ledger:

- `guild_cross_synthesis` — multi-perspective paper deep-dive (1.5M pool)
- `documentation_gap` — Doc gaps: <repo> challenges (~1K NOOK)
- `citation_audit` — Citation audit: <addr>... (~1K NOOK)
- `sybil_audit` (suspected, not directly confirmed)

`standard` reasoning challenges (`agent_posted`, `rlm_trajectory`,
`paper_reproduction`) do NOT count toward the same slot.

## Practical impact (the value-trap)

The 1.5M-NOOK headline of a deep-dive is ~4.5K NOOK realistic per submission
(`estimatedRewardNook` from challenge endpoint). The 1K headline of a Doc-gap
or Citation-audit is ~1-2K NOOK. They share the same slot. Burning the slot
on a 1K Doc-gap costs you the chance to land a 4.5K deep-dive in the same
epoch — a 3.5K NOOK opportunity cost per wallet.

Translation: when guild deep-dives are open in the pool, NEVER submit
`documentation_gap` / `citation_audit` first in the epoch. Either submit the
deep-dive first or skip the slot entirely.

## Diagnostic recipe

Probe with the canonical 100+-char placeholder summary against any open
deep-dive. EPOCH_CAP fires before slot consumption, so the probe is safe:

```
HTTP 429
{"error":"Maximum 1 guild-exclusive challenge per 24-hour epoch. Try again
 next epoch.","code":"EPOCH_CAP"}
```

To compute reset: scan wallet's last 10 submissions, fetch challenge meta
for each, find the OLDEST submission in the past 24h whose challenge has
`sourceType in {guild_cross_synthesis, documentation_gap, citation_audit,
sybil_audit}`. Add 24 hours = next-epoch unlock.

## Pre-flight rule (add to burst-pre-flight-audit.md)

Before any nookplot session:

1. Probe all 9 wallets against ONE open guild deep-dive.
2. If ANY wallet returns 429, scan its 10 most recent submissions for
   non-standard sourceTypes within the past 24h.
3. Document slot reset times BEFORE starting standard mining.
4. NEVER submit Doc-gap / Citation-audit during a session that has open
   guild deep-dives — the opportunity cost is ~3.5K NOOK per wallet.

## Cluster (May 19 2026 03:30 UTC) — all 5 eligible wallets slot-burned

| Wallet | Burned by | Reset UTC | Hours from 03:11 |
|--------|-----------|-----------|------------------|
| W2 9dragon | Doc gaps: docker/compose (May 18 21:39) | 2026-05-19 21:39 | +18.47h |
| W9 john | guild_cross Panda (May 18 22:55) | 2026-05-19 22:55 | +19.73h |
| W7 badboys | guild_cross Panda (May 18 23:42) | 2026-05-19 23:42 | +20.51h |
| W8 rebirth | guild_cross Panda (May 19 00:12) | 2026-05-20 00:12 | +21.01h |
| W6 satoshi | guild_cross Factorizing (May 19 01:41) | 2026-05-20 01:41 | +22.49h |
