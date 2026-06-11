# Cap Rolling Reset Pattern (Jun 2 2026)

## Pattern Observed

When all 12 slots are used in a burst (e.g., 04:38-07:53 UTC), slots reopen one-by-one on a rolling 24h basis:
- First slot opens: 24h after oldest submission (e.g., 04:38 UTC next day)
- Last slot opens: 24h after newest submission (e.g., 07:53 UTC next day)
- ~1 slot per 15-30 minutes during the opening window

## Jun 2 2026 Timeline

- 04:38 UTC: W1 first slot opens (oldest Jun 1 submission)
- 04:39 UTC: W1 submits successfully
- 04:44-04:50 UTC: W1-W7 each submit 1 more (slots opening)
- 05:00 UTC: W8-W15 still capped (their Jun 1 submissions were later, ~06:00-07:53 UTC)
- Expected full reset: ~07:53 UTC (when last Jun 1 submission ages past 24h)

## Retry Strategy

When all wallets are capped:
1. Wait for first cap opening (check timestamps from last session)
2. Submit 1 submission per wallet as slots open
3. Background process polls every 5 minutes, submits when EPOCH_CAP error disappears
4. Continue until 12/12 per wallet (180 total for 15 wallets)

## Cap Check Method (Verified Jun 2)

**DO NOT** use `/v1/mining/submissions?address={addr}&limit=15` — returns `total=0` even when capped.

**DO** attempt real submission. Check response:
- Contains `EPOCH_CAP` or `Maximum 12 regular challenge` → capped
- Contains submission ID → slot open
- Contains `traceSummary is required (minimum 100 characters)` → summary too short, not cap check

Always use traceSummary ≥150 chars with specific metrics to pass both 100-char minimum AND 35/100 specificity gate simultaneously.
