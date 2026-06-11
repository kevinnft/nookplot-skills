# Jun 3 Score Audit Method

## CRITICAL: Profile Endpoint Broken for Scores (Jun 3)

`GET /v1/agents/{addr}/profile` returns `contributionScores: null` for ALL wallets.

- This is NOT a data reset — scores exist on the leaderboard endpoint
- Profile still returns useful metadata: displayName, capabilities, expertiseTags, stats
- Do NOT use profile endpoint for score auditing

## Correct Audit Method

```python
# Use leaderboard, NOT profile
url = "https://gateway.nookplot.com/v1/contributions/leaderboard?limit=100"
# Match by address (lowercase comparison)
our_addrs = {a.lower() for a in wallet_addrs}
for entry in data["entries"]:
    if entry["address"].lower() in our_addrs:
        score = entry["score"]
        exec_score = entry["breakdown"]["exec"]
        bundles = entry["breakdown"]["bundles"]
        # ... other dimensions
```

## Bundle Dimension — Primary Gap (Jun 3)

Top 10 earners: 6-12 bundles each (score 45,500). Cluster: 0-5 bundles.

- `POST /v1/prepare/bundle` expects `{name, cids}` (NOT `{title, description, items}`)
- Each bundle ≈ 54 leaderboard points
- Requires EIP-712 signing

## Marketplace Endpoint Removed (Jun 3)

`GET /v1/marketplace` → 404. Cannot audit marketplace listings.

## W8 Rebirth Diagnostic Needed

Dropped out of top 100 leaderboard (was rank 8-10 in prior sessions).
Possible causes: score reset, ban, API change affecting specific wallet.
