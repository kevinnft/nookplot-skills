# Saturated-Channels Pivot Protocol

When the user issues an aggressive directive ("gas", "fokus wallet N", "maksimalkan semua") AND every reward channel hits its cap simultaneously, the correct response shape is a **status pivot**, not bulk filler work.

## Trigger conditions

All of these true at once:
- submit cap hit (12/12 last 24h)
- post cap hit (10/10 last 24h, `DAILY_CAP`)
- verify queue saturated (every viable solver hits reciprocal-3x or solver-limit-3x)
- learning-post channel exhausted (every verified sub already posted)
- bounty/swarm channels low-ROI (40+ apps each)

## Anti-pattern (observed and denied by user, May 22 2026)

When all the above hit, an attempt to **bulk-store knowledge synthesis** as filler work to "keep producing content" was blocked by the user via tool denial mid-execution. The pattern is wrong because:

1. Knowledge synthesis stored in bursts during a saturation wait is padding, not authorship value — gateway quality scoring penalizes generic synthesis.
2. The user's "gas" directive means "exhaust cap-bound channels" not "manufacture filler in non-cap channels".
3. Bulk synthesis bodies blow up tool I/O (6KB+ python blocks with two large markdown synth bodies) which the user has already said to avoid ("jangan langsung generated post semua kamu kena output length limit").

## Correct pivot output shape

```
W{N} {displayName} | guild #{id} {name} t{tier} {boost}x | stake {amount}
balance {N} NOOK | lifetime {N} NOOK | {V} verified, {NQ} near-quorum, {P} pending

CHANNEL STATUS — semua per-dimension cap hit, tinggal tunggu reset:
  submit_regular   X/12  → next slot {UTC HH:MM} (+{minutes} min)
  submit_guild     X/1   → AVAILABLE | hit
  posting          X/10  → next {UTC HH:MM} (+{hours}h)
  verify_solver_3x hit pada {n} solver di queue
  verify_reciprocal hit pada {addresses}
  knowledge_synth  X/N stored — DITAHAN
  learning_post    X/X verified subs sudah POSTED
  bounty           {n}+ apps each, low ROI
```

Then **present 1-2 numbered options** with concrete actions, not a wall of text. Wait for user pick.

## Why this works

- User gets fresh-audit table (matches USER preference "cek ulang" template).
- ETAs computed from actual data (oldest sub timestamp + 24h rolling), not vague "tunggu nanti".
- Options frame the decision, no filler.
- No background grinding on low-value channels.

## When NOT to pivot

If even ONE cap-bound channel still has slots, keep executing. Pivot only when the whole rolling window is exhausted. Specifically: a guild-exclusive submit slot (X/1) being open is NOT a saturation — push that immediately, don't pivot.

## Cross-reference

- See `inline-pitfalls-may21-2026.md` for related "don't bulk-spam" pitfalls.
- See `sudah-maksimal-eta-reporting.md` for ETA formatting template.
