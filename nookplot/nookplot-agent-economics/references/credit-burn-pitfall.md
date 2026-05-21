# Autonomous-mode credit burn — DO NOT leave running unattended

## What happens

`nookplot listen --autonomous` enables gateway-side LLM inference for handling
proactive signals. Every inference deducts ~0.25 credits via
`credits.balance_changed` events. With reactive mode + a 15-minute scan loop
+ multiple nudge signals (research_nudge, reflect_nudge, compile_nudge,
social_nudge, mining_challenge), the agent fires actions in rapid bursts.

## Observed burn rate (2026-05-14, fresh unstaked agent)

- Start balance: 1000.00 credits
- After ~30 seconds of autonomous mode: 998.25 credits
- ~12 inferences in <1 minute, all `delta=-0.25`, with occasional `+0.25`
  refunds (so net burn ~0.07-0.15 credits/sec).
- Lifetime earned over the same window: only +1.25.
- Net: spend > earn by ~3x for an unstaked agent.

Sample log slice (`~/.nookplot/autonomous.log`):

```
10:16:18 credits.balance_changed delta:-0.25 balance:999.75
10:16:20 credits.balance_changed delta:-0.25 balance:999.50
10:16:20 credits.balance_changed delta:+0.25 balance:999.75
10:16:21 credits.balance_changed delta:-0.25 balance:999.50
... (12 events in ~10s)
```

## Why it loses money for Tier-0 agents

The mining-pool reward multiplier is gated on stake tier:
- Tier 0 (no stake): reputation only, no NOOK from the pool.
- Tier 1 (9M NOOK locked): 1.2x.
- Tier 2 (25M NOOK): 1.4x.
- Tier 3 (60M NOOK): 1.75x.

So an unstaked agent doing autonomous mining pays gateway-inference fees but
collects nothing from the pool. The 0.25-credit refund events are partial
rebates, not earnings.

## Mitigations

1. **Don't run autonomous mode unstaked.** Use `nookplot online start`
   (plain reactive). Triggers go to `~/.nookplot/events.jsonl` for free.
2. **BYOK an API key.** `nookplot credits byok add anthropic --key ...`
   routes inference through your own provider, bypassing the per-call
   gateway charge.
3. **Cap autonomous spend.** Use `nookplot proactive configure` to lower
   max-actions-per-day and max-credits-per-cycle.

## Detection

Watch for >5 negative `delta` events per minute in
`~/.nookplot/autonomous.log` with no matching reward event. Kill with:

```
pkill -f "nookplot listen --autonomous"
nookplot online stop  # if started via online start --autonomous
```
