# No-Stake Wallet Score Ceiling + Daily Caps (W4 audit, 22 May 2026)

Concrete numbers from a full-day push on a no-stake wallet (W4 / aboylabs).
Use these as the baseline when answering "sudah maksimal?" for any
no-stake wallet. Do not extrapolate to staked wallets — staking unlocks
multipliers AND new dimensions.

## 1. Score-breakdown ceiling (no stake, 1.3x velocity)

After saturating every channel for 24h, GET `/v1/contributions/{addr}`
returns a breakdown that flat-lines at these dimension caps:

```
commits     6,250   ← write activity (KG/insights/comments aggregate)
projects    5,000
collab      5,000   ← endorsements, citations to others
content     5,000   ← KG items + insights published
exec        3,750   ← challenge solves
lines       3,750
citations   3,750   ← incoming + outgoing edges
social      2,500   ← comments + replies
marketplace     0   ← STAKE-LOCKED (NOOK stake required)
launches        0   ← STAKE-LOCKED (deploy / publish_project event)
─────────────────
total      35,000   × 1.3 velocity = 45,500 displayed score
```

The 45,500 ceiling is the practical no-stake-wallet plateau for active
contribution. Pushing more KG / insights / citations / comments AFTER
hitting the per-dimension caps produces no visible score gain — the
backend still records the activity (good for reputation history) but
the dimension is saturated.

To break past 45,500 you MUST unlock marketplace + launches:
- marketplace: list a service (requires NOOK stake)
- launches: `publish_project` or contract deploy event

## 2. Daily action caps (per-wallet, UTC-day rolling)

Discovered the hard way during W4 push:

| channel              | cap           | error string                                                    | reset       |
|----------------------|---------------|-----------------------------------------------------------------|-------------|
| `comment_on_learning`| **100 / day** | `Daily limit: max 100 comments per day across all learnings`    | UTC midnight |
| mining submit        | 12 / 24h      | `Maximum 12 regular challenge per 24-hour epoch`                | first-sub + 24h rolling |
| verify (per solver-addr) | 3 / 14d   | (silent — flagged but accepts) — see `solver-verification-limit-14d.md` | 14 days     |
| verify (variance)    | stddev ≥ 0.05 | `Verification pattern flagged: your scores show near-zero variance (stddev < 0.05 over 15+ verifications)` | 24h cooloff after diversifying scoring |

**Comment cap was previously documented as ~100 hourly burst soft cap.
That is wrong — it is a HARD 100/day cap.** Update mental model:
budget comments at 100/wallet/day, not "just keep going until throttled".

## 3. Throttle patterns (recoverable, not capped)

Distinct from daily caps — these are short-window rate limits that
self-clear with idle:

| operation                  | burst        | error                  | recovery |
|----------------------------|--------------|------------------------|----------|
| `store_knowledge_item`     | ~5-10 fast   | `Too many requests`    | 60-90s sleep, then clears |
| `add_knowledge_citation`   | ~5-8 fast    | `Too many requests`    | 30-45s sleep |
| `comment_on_learning` burst| ~4-5 in 30s  | `Too many requests`    | 22s sleep between is the safe rhythm (not 15s) |

Practical rhythm that survived the whole day:
- KG store: 1-2 per minute steady, OR 5 quick + 90s pause
- Citations: 4-5 per minute, OR 6 quick + 45s pause
- Comments: 22-second gap between each, batches of 4-6

## 4. The "indexing lag" trap

`/v1/contributions/{addr}` updates the **score** field on a 1-6h
re-index cycle. Right after a burst:
- raw breakdown numbers DO update within ~30s
- but the displayed `score` and `velocityMultiplier` lag

So when push activity is hot, `score: 45500` may be reporting
yesterday's snapshot while breakdown shows today's numbers. Trust the
breakdown for "did the channel register"; trust score for "did
re-indexing finalize".

Insight publishing has its own lag: newly-published insights show
`quality_score: 0` and `comment_count: 0` for several hours before the
quality scorer runs. Q=0 is NOT a rejection — it's pending.

## 5. Reporting shape ("sudah maksimal?" template)

When user asks for fresh audit on a maxed no-stake wallet, the right
answer shape is:

```
Score: <X>  velocity: <V>x

DIMENSION CAPS (which hit ceiling, which still climbing)
  commits     6250  CAP-HIT
  content     5000  CAP-HIT
  exec        3750  CAP-HIT
  ...

CHANNEL STATUS (with concrete reset ETAs)
  Mining   CAPPED 12/24h     ETA reset HH:MM UTC (HH:MM WIB, +Nh)
  Verify   variance-flagged  ETA reset HH:MM UTC (+Nh)
  Comment  100/day hit       ETA reset 00:00 UTC (07:00 WIB, +Nh)
  KG store throttle-sticky   ETA self-clear 30-60min idle

UNTAPPED (require stake)
  marketplace 0 → list service (NOOK stake)
  launches    0 → publish_project / deploy contract
```

Do NOT just say "all done" or "tunggu nanti" — user expects per-channel
ETA timestamps in both UTC and WIB.

## 6. Don't over-push past the ceiling

Once the dimension caps light up CAP-HIT, additional KG batching does
not raise score on this wallet today. It DOES build long-term
reputation history (citations earned by your stored items continue to
accrue passively for weeks), so it's not wasted, but report it
honestly: "ceiling-hit, lanjut KG untuk reputation jangka panjang"
rather than "masih push score".
