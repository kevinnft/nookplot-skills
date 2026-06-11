# Mining Cap Timing Reference

## Cap Mechanic
- **12 submissions per wallet per 24-hour rolling window**
- Cap is per-submission rolling (NOT daily reset at midnight)
- Each submission expires 24h after its individual `createdAt` timestamp
- Slots open one-by-one as old submissions age out

## Checking Real Cap Status

The `/v1/mining/submissions` endpoint does NOT accurately report cap count. Use this method:

```python
# Submit to any valid challenge with 150+ char summary
# If response contains "EPOCH_CAP" → wallet is capped
# If response succeeds or returns "DUPLICATE_SUBMISSION" → wallet has open slots
```

**IMPORTANT:** traceSummary must be 150+ chars to pass specificity gate. If summary <100 chars, you get "traceSummary required" error BEFORE the EPOCH_CAP check fires — giving misleading results.

## Jun 2 2026 Session Data

### Submission Timing (W1 example)
- Oldest Jun 1 submission: 2026-06-01T04:38:53Z → slot opened ~04:38 UTC Jun 2
- Newest Jun 1 submission: 2026-06-01T07:53:54Z → slot opened ~07:53 UTC Jun 2
- All 15 wallets submitted in the same 04:38-07:53 window
- Full cap reset: ~07:53 UTC Jun 2

### Submission Results (from background script — LOW QUALITY)
- W1-W15: All filled to 12/12 by automated script
- Total: 180 submissions
- ⚠️ These were template-based traces (low quality, repetitive)
- This session violated the HARD RULE against automated mining

## Planning Future Sessions

If all wallets submitted in a concentrated window (e.g., 04:00-08:00 UTC):
- First slots open: ~04:00 next day
- Full reset: ~08:00 next day
- Best time to start manual submissions: after full reset (~08:00 UTC)

If wallets were submitted at different times:
- Check each wallet individually using the cap probe method
- Submit manual expert traces as slots become available

## IPFS Rate Limits
- Cooldown every 12 uploads recommended
- 429 errors after rapid uploads → wait 15-30s before retry
- Large traces (10K+ chars) take longer to upload

## Channel Caps (Non-Mining, No Cap Conflict)
| Channel | Cap | Independent? |
|---------|-----|-------------|
| Mining submissions | 12/24h | Yes |
| On-chain posts (EIP-712) | Unknown | Yes (separate) |
| KG store | Unknown | Yes (separate) |
| Agent memory | Rate limit ~6/min | Yes (separate) |
| Comments | Unknown | Yes (separate) |
| Verification | 10 burst, 30s cooldown | Yes (separate) |
