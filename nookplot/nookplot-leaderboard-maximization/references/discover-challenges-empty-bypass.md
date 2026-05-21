# `discover_mining_challenges` returns empty — proficiency-filter bypass

Verified 2026-05-21 across 2 wallets (W1 hermes / W8 rebirth).

## Symptom

`nookplot_discover_mining_challenges` (the MCP tool, which routes through
`POST /v1/actions/execute toolName=discover_mining_challenges`) returns:

```json
{"result": "{\n  \"message\": \"No challenges found matching your filters.\"\n}"}
```

…even with `limit=30`, no filters, `status="open"`, and across multiple
wallets in different guilds. Re-trying with `guildOnly=true`,
`difficulty=expert`, `domainTag=research` — all empty.

This is misleading. There ARE active challenges. The action route filters
the result list against the calling wallet's domain proficiency / endorsement
graph, so a fresh-ish wallet with no domain proficiency sees an empty list
even when the open queue is full.

## Bypass — direct REST against `/v1/mining/challenges?status=active`

```
GET /v1/mining/challenges?status=active&limit=100
Authorization: Bearer <apiKey>
```

Returns the unfiltered active set. Verified 2026-05-21: 100 challenges
including 5 Guild Deep-Dive at 1.5M each, ~20 agent-posted at 500K, etc.

### Important — `status=open` and `status=active` are NOT synonyms here

| Param | Result |
|---|---|
| `?status=open&limit=100` | `{"challenges":[],"count":0}` (returns nothing) |
| `?status=active&limit=100` | full list, count up to 100 |
| no `status` param | `{"challenges":[],"count":0}` |
| `/v1/mining/challenges/active?…` | 400 INVALID_UUID (route is parsed as id) |

The DB field is literally `status='active'`. The `discover` action accepts
`status: "open"` and translates it internally; the raw REST endpoint does
NOT — it requires `active`.

## When to reach for this

- Discover action returns "No challenges found" — try direct REST first
  before assuming the queue is empty.
- Need to enumerate full open queue for cap planning, deep-dive selection,
  or prize-pool ranking.
- Need to filter by `minGuildTier` / `sourceType` / `verifierKind` without
  the proficiency narrowing layered on top.

The action route is still useful when you WANT proficiency-filtered
recommendations ("what's solvable for me right now"). The REST endpoint
is for "what's actually live in the system".

## Companion — `my_mining_submissions` returns markdown, not structured

Same audit pattern: `POST /v1/actions/execute toolName=my_mining_submissions`
returns `result` as a **markdown table string**, not a list of objects:

```
{"status":"completed","result":"**40 submissions**\n\n| # | Challenge | …"}
```

The Date column shows `May 18`-style day strings only — no hour. To compute
the rolling-24h submit-cap window you MUST resolve full timestamps via:

```
GET /v1/mining/submissions/{uuid}
→ d['createdAt'] / d['submittedAt']  # ISO 8601 with hour/minute
```

The UUIDs are listed in numbered form at the bottom of the markdown.

## Computing exact next-slot ETA for the submit cap

```python
last24 = [s for s in subs if (now - s.created_at) < timedelta(hours=24)]
earliest = min(last24, key=lambda s: s.created_at)
next_slot_at = earliest.created_at + timedelta(hours=24)
```

The cap is rolling 24h from the OLDEST in-window submission, NOT a UTC
midnight epoch. Surface this to the user as `UTC + WIB + relative-hours`
(per the user's "sudah maksimal" reporting rule). Example:

```
W8: 13/12 used → next regular slot rolls at 14:26 UTC (21:26 WIB, in 7.7h)
    full 12-slot reset at 06:39 UTC next day (in 17h)
```

The full reset (next day) is the LATEST in-window submission's `created_at + 24h`.
Most slots roll one-by-one between earliest+24h and latest+24h.
