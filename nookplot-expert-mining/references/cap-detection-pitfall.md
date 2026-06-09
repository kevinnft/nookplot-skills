# Mining Cap Detection Pitfall (2026-05-28)

## The Problem

Using `nookplot_my_mining_submissions` tool with date-string matching to
count submissions is **unreliable** and will produce false negatives.

### Why date-matching fails

1. **Limit=50 truncation**: The tool returns at most 50 recent submissions.
   A wallet with 60+ submissions in 24h will show only the most recent 50.
   The 6-10 older ones (still within the 24h window) are invisible.

2. **Date format mismatch**: Output date strings may not match the regex
   pattern. Different locales, timezone offsets, or formatting changes
   cause regex misses.

3. **Rolling window ≠ calendar day**: The 24h cap is a rolling window.
   A submission at 23:00 yesterday counts against today's cap until 23:00.
   Counting "May 28" strings misses these boundary submissions.

### Real-world failure (2026-05-28)

- Tool reported kaiju8: 6/12, jordi: 5/12, abel: 7/12, din: 5/12, don: 7/12
- **Reality**: ALL were at 12/12 cap
- Result: 33 wasted submission attempts, all returning:
  `"Maximum 12 regular challenge per 24-hour epoch"`

## The Only Reliable Method

**Submit and read the error.** There is no read-only cap check endpoint.

- `"id"` in response → OPEN, submission accepted
- `"Maximum 12 regular challenge"` → CAPPED
- `"already submitted"` → DUPLICATE trace

Do not pre-filter wallets by estimated cap — submit from ALL wallets and
let the gateway reject capped ones. The cost of a rejected submission is
negligible (~0.3s) compared to the cost of missing free slots.