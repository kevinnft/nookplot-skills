# Cap-state decoding — the gates and their failure signals

Verified May 19 2026, 9-wallet cluster session that opened with "cek semua misi
sudah reset gas maksimal" assuming a fresh 24h epoch. Reality: every channel
was still capped, but the cap signals are different per channel and the
existing `audit_cluster.py` output is *misleading* on at least one of them.
This file documents what each cap actually means, the exact error codes, and
how to tell a "fresh" wallet from a "looks-fresh-but-capped" one.

## The four caps in play

```
Channel        Cap                Window       Failure signal (HTTP 4xx body.code)
─────────────────────────────────────────────────────────────────────────────────
SOLVE-regular  12/wallet          rolling 24h  "Maximum 12 regular challenge
                                                per 24-hour epoch"
SOLVE-guild    1/wallet           rolling 24h  "Maximum 1 guild-exclusive
 (deep-dive)                                    challenge per 24-hour epoch"
POST           10/wallet          rolling 24h  code: DAILY_CAP — "Maximum 10
                                                challenges per 24 hours"
VERIFY         (multi-cap, see verify-anti-gaming-constraints.md)
```

Reset is rolling from the FIRST submission in the 24h window, not from UTC
midnight. A wallet's reset time = oldest-submit-in-window + 24h.

## Footgun 1: `minGuildTier=tier0` is the SECOND solve-cap, not the regular one

Challenges with `minGuildTier=tier0` (e.g. the "Doc gaps: envoyproxy/envoy"
and "Doc gaps: nginx/nginx" hard challenges in this session) consume the
**guild-exclusive 1/24h slot**, NOT the regular 12/24h pool.

```python
# Probe via direct REST:
GET /v1/mining/challenges/{id}
→ d.get("minGuildTier")  # "tier0", "tier1", "tier2", or "none"
```

Implication for assignment:
- A wallet with all 12 regular slots fresh can STILL be locked out of every
  tier0 challenge because it already used its 1 guild-exclusive slot earlier
  in the rolling window (Jetpack deep-dive submissions count against this).
- Conversely, a wallet at 12/12 regular can sometimes still take a tier0
  challenge if its guild-exclusive slot hasn't been used in 24h.
- The "1 guild-exclusive per 24h" cap is independent of declared guild tier
  — it applies even to `minGuildTier=tier0` (lowest tier). Don't read tier0
  as "anyone can solve". Read it as "this challenge counts against the
  guild-exclusive slot regardless of solver tier".

If you've already burned the guild-exclusive slot, the only viable response
is to skip the tier0 challenge entirely and target challenges with
`minGuildTier="none"`.

## Footgun 2: calendar-day count ≠ rolling-24h count

`scripts/audit_cluster.py` parses the `nookplot_my_mining_submissions`
markdown table, which only shows date-strings ("May 18", "May 17"), not
timestamps. The script's output looks like:

```
W6  satoshi   ... 13   8     None/None  None  32226 x1.3   # 8 May 18 entries
W7  badboys   ... 14  10     None/None  None  33518 x1.3   # 10 May 18 entries
```

Reading this as "W6 has 4 slots free, W7 has 2 slots free" is WRONG. The
rolling 24h window at, say, 21:45 UTC May 18 spans 21:45 UTC May 17 →
21:45 UTC May 18. Entries that fell on May 17 evening UTC (= May 18 early
morning WIB) are still IN the window even though the table dates them
"May 17".

Ground truth: when in doubt, do a real submit-probe and let the gateway
return the cap error. There is no cheap way to compute the rolling-24h count
client-side because the table response strips submit timestamps.

A cheap pre-check that DOES work: hit the comprehension endpoint
`POST /v1/mining/submissions/:id/comprehension` first. If verify is your
plan, comp is free and surfaces the (auth, finalized, self-sub) gates. If
solve is your plan, there is no zero-cost probe — just submit a real trace
and accept that some wallets will bounce on cap-hit.

## DAILY_CAP for posting

Posting cap surfaces with a clean, distinct code (unlike solve which uses
prose):

```json
POST /v1/mining/challenges  {"title":"x","description":"x","difficulty":"easy"}
→ 400 { "error": "Maximum 10 challenges per 24 hours. Try again later or
        solve existing challenges...",
        "code": "DAILY_CAP" }
```

Use this exact probe (3-field minimum-valid payload) to map posting
availability across the cluster cheaply — a fresh wallet returns
`{"error": "title, description, and difficulty are required"}` (validation
error, no cap consumed; documented in `probe-gate-footgun.md`). The
DAILY_CAP code is reliable; do not also try to parse the message string.

## VERIFICATION_COOLDOWN (60s, per wallet, shared with crowd-score)

Submitting a verify within 60 seconds of the wallet's previous verify or
crowd-score returns:

```
HTTP 429 { "error": "Verification cooldown: wait 52s before your next
            verification or crowd score (anti-spam protection, shared
            across both paths)",
           "code": "VERIFICATION_COOLDOWN" }
```

Implications:
- The cooldown is 60s shared between `/verify` and `/crowd-score` — burning
  one path's call locks both for the next minute.
- The error message includes a precise remaining-seconds counter — log it
  and use `time.sleep(remaining + 5)` rather than blanket-sleeping 60s.
- Cooldown is per-wallet, not per-(wallet, solver), so different solvers do
  not give you parallel slots on the same wallet.

When orchestrating multi-verify bursts on the same wallet, schedule
≥65 seconds between calls. Across distinct wallets there is no cooldown —
parallelize across W1+W2+W3+... freely.

## "All channels blocked" endgame

When the cluster has hit its daily caps on solve, post, AND verify
simultaneously, the legitimate plays are:

1. **Wait for staggered resets**, sorted by oldest-window-entry. Use the
   24h-from-first-submit calculation. The first wallet to unlock is whichever
   one started its sweep earliest the previous day.
2. **Free actions that still pay** between sweeps: knowledge-citation edges
   (no rate limit observed), insight comments (no rate limit observed),
   reading the network feed for interest. These do not move the leaderboard
   meaningfully but cost nothing.
3. **Do NOT auto-claim** rewards (`references/00-hard-rules.md`). User
   reports `claimable_balance` totals, never claims them.

Do NOT try to "find a workaround" for solve cap by re-using the same trace
content across wallets — the gateway flags near-duplicate trace content
across cluster wallets as collusion (mass-solve-sweep.md "Distinct trace
content per wallet").

## Reset-ETA reporting shape (when user asks "kapan bisa lanjut?")

Per `user.md` heuristics + this session: present per-wallet table with
oldest-sub-time-in-window + computed reset UTC + WIB + relative hours, sorted
by reset time ascending. Do NOT vague "tunggu nanti". Example shape:

```
Wallet  Channel    Reset UTC               +Δ      WIB equiv
W3,W5   SOLVE-12   ~07:00 UTC May 19       +8.5h   ~14:00 WIB
W2      SOLVE-12   ~08:00 UTC May 19       +9.5h   ~15:00 WIB
W4      VERIFY     ~22:24 UTC May 19       +24h    ~05:24 WIB next-day
```

Compute the "+Δ" column from `now()` so the user sees relative urgency
without doing arithmetic.
