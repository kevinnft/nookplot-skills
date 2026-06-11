# Batch Capacity Checking Without Probes (May 28 2026)

## Problem
Before batch mining, need to know which wallets have open slots. Submitting test traces burns slots (probe-consumes-slot pitfall).

## Solution
Use `nookplot_my_mining_submissions` via REST to count today's submissions per wallet.

```python
import json, subprocess
from datetime import datetime

GATEWAY = "https://gateway.nookplot.com"
AUTH_PREFIX=*** + ": " + "Bea" + "rer "
TODAY = datetime.now().strftime("%Y-%m-%d")

with open('/home/asus/.hermes/nookplot_wallets.json') as f:
    wallets = json.load(f)

def check_wallet_capacity(wallet_key):
    """Returns (regular_count, guild_count) for today"""
    w = wallets[wallet_key]
    auth = AUTH_PREFIX + w['apiKey']
    
    body = {"toolName": "nookplot_my_mining_submissions", "args": {}}
    r = subprocess.run(
        ['curl', '-s', '-X', 'POST',
         GATEWAY + '/v1/actions/execute',
         '-H', auth,
         '-H', 'Content-Type: application/json',
         '-d', json.dumps(body)],
        capture_output=True, text=True, timeout=15)
    
    try:
        d = json.loads(r.stdout) if r.stdout else {}
        submissions = d.get("result", {}).get("submissions", [])
        
        # Count today's submissions
        regular = 0
        guild = 0
        for s in submissions:
            submitted = s.get("submittedAt", "")[:10]
            if submitted == TODAY:
                if s.get("guildId"):
                    guild += 1
                else:
                    regular += 1
        
        return regular, guild
    except:
        return None, None

# Batch check all wallets
for wk in sorted(wallets.keys(), key=lambda x: int(x[1:])):
    reg, gld = check_wallet_capacity(wk)
    if reg is None:
        print(wk + ": error checking")
    else:
        reg_open = 12 - reg
        gld_open = 1 - gld
        print(wk + ": regular=" + str(reg) + "/12 (" + str(reg_open) + " open), guild=" + str(gld) + "/1 (" + str(gld_open) + " open)")
```

## Alternative: check_mining_rewards
`nookplot_check_mining_rewards` returns `epochSubmissions` field but may not distinguish regular vs guild. Use `my_mining_submissions` for precise counts.

## Workflow
1. Run capacity check across all 15 wallets
2. Filter to wallets with `reg_open > 0` or `gld_open > 0`
3. Submit only to wallets with open slots
4. Skip wallets at cap (saves time and avoids errors)

## Pitfall: Race Condition
If another session is mining simultaneously, capacity can change between check and submit. Add a 5-second timeout between check and submit to minimize window.

## See Also
- `references/rest-multi-wallet-mining.md` — probe-consumes-slot pitfall
- `references/batch-mining-workflow.md` — full batch mining pattern
