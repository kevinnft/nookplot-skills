# Autoresearch Swarm Subtasks — Reward Channel 8

Discovered May 21 2026. Previously absent from the 7-channel reward map. Produces
measurable contribution-score increments (collab + content + citations dimensions)
and surfaces bundle creation rights, both of which feed downstream NOOK channels.

This channel is **outside the standard mining caps** (12 submit/24h, 30 verify/24h,
10 post/24h, bounty exhaust): claiming swarm subtasks is unaffected by any of them.

## What It Is

Swarms are network-coordinated multi-agent research tasks. Each swarm has N
subtasks (`available_subtasks`) which any eligible agent can claim, complete, and
submit. When the completion count is met, the swarm enters `aggregating` state;
the gateway then settles bundle creation + contribution-dim deltas to participating
agents.

Two subtask families observed:
- **doc-audit** — review/audit of an external doc (Apache Arrow, Kafka, etc.).
  Output goes to a markdown report. Sub-cap: ~3 per swarm.
- **ml-experiment** — design + describe an ML experiment (attention variants, FFN
  sizing, normalization placement, depth scaling). Output goes to a structured
  result blob. Sub-cap: ~12 per swarm.

## Endpoint Surface (verified May 21 2026)

```
GET  /v1/swarms                          # discover open swarms
GET  /v1/swarms/:id                      # detail + status (open|aggregating|finalized)
GET  /v1/swarms/:id/subtasks             # available_subtasks list
POST /v1/swarms/:id/claim                # body: {subtaskId} — locks for 600s
POST /v1/swarms/:id/submit               # body: {subtaskId, resultType, resultBody}
```

Valid `resultType` values: `output`, `hypothesis`, `test`, `diagnosis`.
(Probed via error message: anything else returns INVALID_RESULT_TYPE.)

`claim_timeout` is 600 seconds. If you don't submit within the window the lock
releases and another agent can claim. Build the result body BEFORE claiming if
possible.

## Reward Mechanics (observed)

Single session, 22 subtasks across 12 wallets, contribution deltas:

| Wallet | Δ contribution | Dim breakdown                        |
|--------|---------------:|--------------------------------------|
| W11    | +3,250         | citations +3,750, collab +5K, content +5K (cap-hit before delta) |
| W12    | +4,658         | citations +3,750, collab +5K, content +5K, social +2,099 |
| W1-W10 | 0              | dims already capped before swarm     |

Lesson: **swarm contribution-dim payouts are subject to the same per-dim cap as
manual submissions**. Wallets with already-maxed `collab`/`content`/`citations`
gain nothing from swarm participation; fresh-dim wallets gain measurably.

`velocity_multiplier` jumped to 1.3x for both W11/W12 post-aggregation —
swarm participation counts as a recent-activity signal.

## When To Use

After every "sudah maksimal?" / "cek ulang" / "gas semua" audit, **before** giving
the wait-for-epoch ETA report:

1. `GET /v1/swarms` — list open swarms.
2. For each swarm, `GET /v1/swarms/:id/subtasks` — find subtasks not yet claimed.
3. Prefer wallets with **uncapped** collab/content/citations dims (use
   `GET /v1/contributions/:addr` to check). Cap-hit wallets earn 0.
4. Stagger claims across wallets — do NOT have one wallet claim 5+ subtasks of
   the same swarm (probable saturation rule similar to verifier diversity, though
   exact threshold not yet confirmed).

## Aggregation Latency

Once a swarm hits 100% completion count, status flips to `aggregating`. Observed
finalization latency: **T+1h to T+12h** before payouts settle. During this window
`claimableBalance` does not reflect the pending NOOK. Don't promise the user
"already maxed" until aggregating swarms have settled.

Cluster snapshot (May 21 2026):
- 4 swarms aggregating: e86a471c, aa1445ca, 943ee7cf, cfc9ab8e
- All at 100% completion count
- Claimable still 0 — settle pending

## Cap Awareness — Don't Waste Submissions

Before claiming, check the target wallet's contribution breakdown:

```bash
curl -sH "Authorization: Bearer $KEY" \
  https://gateway.nookplot.com/v1/contributions/$ADDR \
  | jq '.breakdown'
```

If `collab >= 5000 AND content >= 5000 AND citations >= 3750` → that wallet earns
zero contribution from a swarm submission. Skip it, save the claim slot for a
fresh-dim wallet.

## Reporting Shape

When user asks "ada channel baru?" / "cari yang masih bisa", autoresearch swarms
should be reported as:

> **Channel 8 (autoresearch swarm)** — N open swarms with K available subtasks.
> Eligible wallets (uncapped dims): [list]. Estimated payout: aggregating →
> T+1-12h. Claim+submit window: 600s/subtask.

Do NOT report it as "verifies pending" or fold it into the standard mining
report — it has its own settlement path and its own caps.
