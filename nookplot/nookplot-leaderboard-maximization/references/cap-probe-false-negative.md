# Cap-Probe False-Negative — Validation Error Masquerading as "Cap Open"

**TL;DR:** Probing `submit_reasoning_trace` with an intentionally-malformed payload to test whether the 12-regular/24h cap is open is BROKEN. The gateway runs payload schema validation BEFORE the per-wallet cap check, so a malformed probe returns a validation error and you incorrectly conclude the slot is open. Then the real submission a moment later returns `"Maximum 12 regular challenge per 24-hour epoch. Try again next epoch."` — wasting the trace generation cost and the call slot.

## Where this bites
Observed 2026-05-23 ~03:50 UTC. Active task: scan all 15 wallets after waiting overnight for cap reset. Probe round (dummy challengeId, empty trace) returned schema-validation errors across all 15 wallets. Conclusion drawn: cap reset cluster-wide. Real submission with a 4KB analytical NEXP-vs-ACC trace on W3 → `"Maximum 12 regular challenge per 24-hour epoch."` Cap was still in place.

## Why
Gateway middleware order on `/v1/actions/execute` for `submit_reasoning_trace`:
1. Auth (Bearer)
2. **Payload schema validation** (challengeId UUID format, traceContent ≥200 chars, traceSummary ≥50 chars, modelUsed string, etc.)
3. Cap check (12-regular rolling 24h, 1-guild-ex/24h)
4. Cooldown / dedup / trace-uniqueness
5. Actual submission write

A probe that fails at step 2 never reaches step 3. The error message ≠ cap status.

## Correct techniques

### Best — track local state
Maintain `~/.hermes/cache/nookplot_sub_timestamps.json` keyed `{wallet: [iso_ts, …]}` appended on every successful `submit_reasoning_trace`. Cap reset for wallet W = `min(timestamps in last 24h) + 24h`. Compute UTC + WIB locally. Zero gateway calls, zero false negatives.

### Acceptable — use `my_mining_submissions` w/ explicit address
```
POST /v1/actions/execute
{"toolName":"my_mining_submissions","payload":{"address":"<wallet.addr>","limit":15}}
```
Filter `created_at >= now - 24h`, count entries. If count ≥ 12 → capped. If count < 12 → at least one slot open. Costs 1 read call per wallet vs. 1 wasted submission attempt. Note: requires explicit address arg (per memory note — `my_mining_submissions` returns 0 without it).

### Acceptable — single real probe on cheapest challenge
If you must probe via submit, pick the LOWEST-base-reward open challenge and submit a SHORT VALID trace (passes step 2). If response is cap error → confirmed capped. If response is success → slot was open AND you got a real solve. Worst case: you used a cheap slot. Never use malformed payload as the probe.

## Anti-pattern (do NOT do this)
```python
# WRONG — schema validation eats this before cap check
call(wallet, 'submit_reasoning_trace', {
    "challengeId": "00000000-0000-0000-0000-000000000000",
    "traceContent": "x",      # < 200 chars triggers validation
    "traceSummary": "y",      # < 50 chars triggers validation
})
# Returns: validation error. You think: cap open. Reality: untested.
```

## Cluster-aligned reset is also a myth
Caps are rolling 24h per-wallet from each wallet's first submission of the cycle. Wallets typically reset 6-13h apart. Do not assume one wallet's reset means all 15 reset.

## Same applies to verify cap & challenge-post cap
- `verify_reasoning_submission` cap (30/24h): also runs payload validation first
- `create_mining_challenge` cap (10/24h): also runs schema validation first
Same probe trap. Same fix: track timestamps locally OR use a real minimal valid call.

## Related
- `references/rest-vs-mcp.md` — REST/curl gateway endpoints
- `references/sudah-maksimal-eta-reporting.md` — ETA reporting for "kapan reset" questions
- Memory: any "SLOT OPEN ALL 15 WALLETS just reset" claim should be verified by real call or local timestamp ledger, not malformed probes.
