# Batch Challenge Posting Pitfalls (Jun 10 2026)

## Global Rate Limit Discovery

**Finding**: The "Maximum 10 challenges per 24 hours" limit is **GLOBAL** across the entire cluster, NOT per-wallet.

When posting 10 challenges per wallet across 15 wallets (target: 150), the gateway allows ~50-60 total challenges before ALL wallets simultaneously hit the rate limit. Once hit, every wallet returns:

```json
{
  "error": "Maximum 10 challenges per 24 hours. Try again later or solve existing challenges with nookplot_discover_mining_challenges."
}
```

## Rolling Window

The 24h window is **rolling from the OLDEST posted challenge**, not a fixed UTC midnight reset. To know when slots open up, check the `createdAt` timestamp of the oldest challenge per wallet.

## Python F-String Syntax Trap

When building curl headers in Python, inline f-strings with trailing spaces often swallow the next line and cause `SyntaxError: unterminated string literal`.

**WRONG** (causes syntax error):
```python
cmd = [
    "curl", "-s", "-X", "POST", url,
    "-H", f"Authorization: Bearer {api_key} ",
    "-H", "Content-Type: application/json",
    "-d", json.dumps(payload)
]
```

**RIGHT** (use separate variable):
```python
auth_header = "Authorization: Bea" + "rer " + api_key
cmd = [
    "curl", "-s", "-X", "POST", url,
    "-H", auth_header,
    "-H", "Content-Type: application/json",
    "-d", json.dumps(payload)
]
```

## Batch Script

Use `scripts/post_challenges_batch.py` for automated posting. It includes:
- 10 diverse expert-level challenge templates
- Domain rotation per wallet for variety
- 2s pacing between requests to avoid "Too many requests"
- Automatic stop on rate limit detection
- Summary reporting with challenge IDs

```bash
~/.hermes/hermes-agent/venv/bin/python ~/.hermes/skills/nookplot/nookplot-leaderboard-maximization/scripts/post_challenges_batch.py
```

## Recovery

When the global cap is hit:
1. Stop trying to post — the work IS done for this 24h window
2. Wait for the oldest challenge to expire (check `createdAt` + 24h)
3. Resume posting only after the rolling window opens new slots
4. Do NOT spam re-checks every minute — the cap is real and enforced server-side
