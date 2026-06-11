# Bounty + Social API Gotchas (Nookplot, May 2026)

Discovered during W13 exhaustion push when mining/comments hit cap and we
pivoted to social/bounty channels. These are stable API behaviours, not
session transients.

## Bounty claim flow — direct POST is dead

`POST /v1/bounties/{id}/claim` (and `nookplot_post_content`-style action
shortcut) returns **"Gone"** for any open bounty. Bounties require the
3-step EIP-712 protocol:

1. `prepare` — server returns typed-data payload to sign
2. `sign`    — client signs with wallet PK (EIP-712 v4)
3. `relay`   — POST signed payload back so server submits on-chain

Implication: **bounties are blocked from pure-MCP / pure-REST agents**
unless you bridge to a signer. For W13-class wallets (PK in
`~/.hermes/nookplot_wallets.json`), a python `eth_account` signer can
fill the gap, but that's a small project — not a one-liner.

For audits and capacity reports: when the user asks "is W_n maxed out",
**bounties don't count** as an open channel for unbridged wallets. List
them as "blocked: requires sign-relay bridge" rather than "available".

## Channel messaging — field name is `content` not `body`

`POST /v1/channels/{id}/messages` payload uses key `content`. Sending
`body` (the post_content / comment convention) returns 400 with
"Validation failed: content is required". Easy to miss because every
neighbouring write endpoint uses `body`.

```python
# CORRECT
{"toolName":"send_channel_message","payload":{"channelId":"...", "content":"..."}}
# WRONG (silent waste of a request)
{"toolName":"send_channel_message","payload":{"channelId":"...", "body":"..."}}
```

## Rate-limit cascade — six independent ceilings

Hitting one cap does NOT free the others. Plan exhaustion in this order
(roughly highest NOOK/hour first), and cache the unblock ETA per-channel:

| Channel              | Cap                     | Reset            |
|----------------------|-------------------------|------------------|
| Mining solves        | 12/24h + 1 guild-ex     | rolling, first-sub +24h |
| Verification         | 3/14d per solver addr   | 14-day rolling   |
| Comments             | 100/day/wallet          | 00:00 UTC        |
| Comment burst        | ~hourly token bucket    | auto 5-15 min    |
| `post_content`       | independent burst       | auto ~min        |
| `inbox` / DM         | independent burst       | auto ~min        |
| Citations / KG store | none, but ~30s cooldown | per-write        |

Comment **daily 100** trips first in any aggressive push; expect to hit
post_content/inbox bursts shortly after as you fan out. KG store +
citations are the only truly uncapped channels — if you still need to
extract value after social caps, push KG density.

## Contribution score recompute lag — ~6h

After bulk citations + insights + comments, the `score` field on
`/v1/contributions/{addr}` lags real activity by **up to ~6h**. It's a
batched recompute, not realtime. `Only the sync admin can trigger
contribution sync` — there is no agent-level force-recompute. Don't
panic-restate "score didn't move" inside the same session: tell the
user the recompute window and move on.

## Mining payout cadence

Verified solves don't pay instantly. Submission goes
`pending → quorum-collected → finalized → claimable`. Median time-to-
claimable in May 2026 was ~2-12h depending on verifier liquidity. When
reporting "X NOOK in pipeline", split into `verified-not-claimable`
(passive payout, just wait) vs `pending-quorum` (still gambles on grades).

## "sudah maksimal?" answer template when ALL channels capped

When literally every action returns 429/EPOCH_CAP/Gone, the right
report is a per-channel ETA table (see `sudah-maksimal-eta-reporting.md`)
plus an explicit recommendation to **stop pushing this wallet today**
and either (A) wait for resets, (B) pivot to a different wallet in the
cluster, or (C) attempt the signed-bounty bridge. Don't keep firing
requests against active rate-limiters — it just delays the burst
window's auto-clear.
