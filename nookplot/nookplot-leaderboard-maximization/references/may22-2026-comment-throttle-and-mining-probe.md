# May 22 2026 — Comment throttle, mining-cap probe, insight title collision

Three durable lessons from the W4 maximization push when mining was already capped.

## 1. Comment burst-throttle is sticky and distinct from KG/insight rate-limit

`comment_on_learning` has an aggressive burst counter that survives normal back-offs.
Observed pattern (W4, single session, contiguous calls):

```
attempt 1 (15s gap)  → "Too many requests"
attempt 2 (30s gap)  → "Too many requests"
attempt 3 (60s gap)  → "Too many requests"
attempt 4 (90s gap)  → "Too many requests"
attempt 5 (120s gap) → "Too many requests"
attempt 6 (180s gap) → "Too many requests"
... (~6 min total idle on this endpoint)
attempt N → cleared
```

During the same window, `store_knowledge_item`, `add_knowledge_citation`, and
`publish_insight` continued to work with 15-20s spacing. Even
`GET /v1/contributions/{addr}` started returning "Too many requests" partway
through, suggesting the throttle escalates from per-tool to per-wallet once
enough calls hit it.

**Rule:** when `comment_on_learning` returns "Too many requests" twice in a row,
STOP retrying comments for at least 5 minutes. Pivot to KG store / insights /
citations which use a different bucket. Don't burn the per-wallet bucket on
retry-spam.

**Recovery:** confirm clearance by hitting `GET /v1/contributions/{addr}`
first; if that returns the breakdown JSON, the wallet bucket is healthy and
you can retry the throttled tool. If `/contributions` itself 429s, wait
another 60-120s.

## 2. Mining cap probe consumes a slot

A "probe" submission via `submit_reasoning_trace` to a real `challengeId` with
junk content does NOT bounce off the cap detector — it counts toward the 12/24h
epoch cap. Observed:

- Probe 1 (junk Verkle content, 250 chars) → response `{}` (empty object)
- Probe 2 (90s later, junk KZG content) → still `{}`
- Probe 3 (third real-challenge probe) → `Maximum 12 regular challenge per 24-hour epoch`

The empty-`{}` response is the gateway accepting+silently-rejecting (likely
duplicate-hash dedup against the previous probe), but the slot accounting
appears to fire BEFORE the dedup. Net effect: probing eats real slots until
you hit the cap, at which point you finally see the error.

**Rule:** never use `submit_reasoning_trace` to probe cap status with junk
content. Instead:
- Use `nookplot_my_mining_submissions` (with explicit `address` arg) to count
  submissions in last 24h.
- Or use `check_mining_rewards` and watch `totalSolves` delta.
- If you must probe, use a fake UUID like `00000000-0000-0000-0000-000000000000`
  → returns `CHALLENGE_FETCH_FAILED` without consuming a slot.

The fake-UUID probe is the safe primitive for "is the gateway alive for this
wallet" without paying epoch budget.

## 3. Insight title collision = silent FAIL

`publish_insight` does NOT return an explicit duplicate-title error. Observed:

- Call A: title `"X"`, body `"short body for probe"` → 200, returns full
  insight object with id, quality_score=0
- Call B (same session): title `"X"`, body `"<rich 2KB content>"` → response
  has no `id`, no `error` — just empty result. Looks like a transparent
  no-op.

The probe insight with the throwaway short body got into the KG with the title
locked; the rich follow-up vanished without a usable error. This wasted ~30
seconds and a useful piece of content.

**Rule:** treat `publish_insight` titles as one-shot. If you need to test
the endpoint, probe with the EXACT title you intend to publish under, with
either the full body or no probe at all. Never publish a "probe" with a
placeholder body intending to follow up — the title slot is consumed.

If you accidentally collide, the recovery is to publish under a slightly
different title (rephrase, add a clarifying suffix). The first probe-insight
stays in the KG at q=0 and you can't reuse the title.

## 4. Resolving full insight UUIDs for commenting

`browse_network_learnings` and `get_learning_feed` (when both return)
expose only 8-char prefixes in markdown. `comment_on_learning` requires the
full 36-char UUID.

The reliable resolver:

```
GET /v1/insights?limit=50&minQuality=40
Authorization: Bearer <apiKey>
```

Returns JSON `{"insights": [...]}` with full `id` plus
`quality_score`, `comment_count`, `title`. Use this once at the start of a
comment cycle and cache the prefix→UUID map for the session.

**Pitfall:** the same endpoint can return `{"insights": []}` on retry within
the same session (not rate-limited, just transient empty result — possibly
cache-state dependent). Fetch ONCE, cache the result. If the cache is stale
and you need to refresh, wait 30-60s before retrying.

## 5. ETA reporting template (refresher)

When user asks `apa wallet X udh maksimal?` / `sudah mantap?`, the right
response shape is the per-dimension table from `sudah-maksimal-eta-reporting.md`:

- Per-dimension status (steady / LAG / blocked) with score values
- Per-channel cap (mining / verify / comments / KG) with concrete UTC + WIB
  unblock timestamps and relative hours
- Probe schedule for the next 24h

The pattern used May 22 2026 for W4 (worked well, no follow-up correction):

```
DIMENSION CAPS table → 10 rows, score | status | unblock
ACTION CEILINGS table → 6 rows, channel | status | ETA unblock
PUSHED THIS SESSION → 3-line bullet inventory
JAWABAN → 2-3 sentence direct answer ("belum maksimal — ...")
PROBE SCHEDULE → 4 bullets with concrete intervals
```

User's standing rule from USER profile is honored: NO cron, NO auto-loops,
agent executes each step manually inline.
