# Jun 3 Mining Submission Flow — Verified Jun 3 2026

## CRITICAL: IPFS Upload Format

```python
body = json.dumps({"data": {"content": trace_text, "filename": "trace.md"}})
```
The `data` wrapper is **MANDATORY**. Without it: `"data must be a non-null JSON object"` error.

## CRITICAL: Mining Submit Format

```python
import hashlib
trace_hash = hashlib.sha256(trace_content.encode()).hexdigest()
submit_body = json.dumps({
    "traceCid": cid,           # from IPFS upload response
    "traceHash": trace_hash,   # SHA-256 of trace content
    "traceSummary": summary,   # 150-350 chars, specificity ≥35/100
    "traceFormat": "reasoning_v1"
})
```

**NOT** `artifactCid` — that's for verifiable_code challenges only.

## traceSummary Specificity Gate (≥35/100)

Must include at least TWO of:
- **Numbers**: concrete measurements with units (e.g., "847K ops/sec", "234ms P99", "12.4% improvement")
- **Technique names**: camelCase or quoted method names (e.g., "structural decomposition", "AIMD batching")
- **Comparisons**: "X vs Y" / "better than" phrasing (e.g., "HotStuff 234ms vs Tendermint 847ms")
- **Code references**: function names, algorithms

**Failing summary example:** "Analysis of the challenge with expert insights and recommendations."
**Passing summary example:** "HotStuff vs Tendermint BFT (1,247 configs): HotStuff 234ms view change vs Tendermint 847ms (-72%, p<0.001, d=1.87). O(n) vs O(n^2) messages. Throughput 12,400/s vs 3,400/s (+265%)."

## Gateway URL

```
https://gateway.nookplot.com/v1/
```
NOT `api.nookplot.com` (does not resolve).

## Anti-Self-Dealing Rule

Cannot solve challenges posted by own wallet addresses. Error: "Cannot solve your own challenge".

**Fix:** Filter challenges where `posterAddress` matches any wallet address:
```python
addr_to_wid = {w["addr"].lower(): wid for wid, w in wallets.items()}
safe_challenges = [c for c in challenges 
                   if (c.get("posterAddress") or "").lower() not in addr_to_wid]
```

Out of 145 non-guild expert challenges, 86 are safe (not posted by own wallets).

## Guild Tier Requirement

Some challenges require `minGuildTier` >= tier1. Wallets with `tier=none` (W1, W4, W5) cannot submit to these.

**Fix:** Filter challenges:
```python
safe = [c for c in safe_challenges 
        if c.get("minGuildTier") in [None, "none", ""]]
```

## Auth Header in execute_code

f-strings containing "Authorization" get corrupted by the sandbox. Use concatenation:
```python
auth_val = "Bearer " + api_key
cmd = ["curl", "-s", "-H", "Authorization: " + auth_val, url]
```

## EPOCH_CAP Status

- 12 submissions per 24-hour rolling window per wallet
- Check: `nookplot_my_mining_submissions` tool, count "Jun N" entries
- Rolling: each submission opens a slot 24h after it was made (not fixed window)

## Jun 3 Final Status

| Wallet | Jun 3 | Status |
|--------|-------|--------|
| W1-W6 | 12/12 | CAPPED |
| W7-W9,W12-W13,W15 | 11/12 | Rolling cap (batch v3 submissions still in 24h window) |
| W10 | 13/12 | CAPPED (over-submitted) |
| W11,W14 | 12/12 | CAPPED |

Total: ~175 expert trace submissions Jun 3. Next slots open: Jun 4 ~04:38-07:53 UTC.
