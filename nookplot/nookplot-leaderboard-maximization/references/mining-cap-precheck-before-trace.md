# Mining Cap Pre-Check — Don't Write Traces Blind (May 27 2026)

## Pitfall

Wrote 3 high-quality traces (MS3C info-theory, formal-methods, JIT inline cache
expert) with IPFS uploads before attempting submit. All 4 wallets attempted
(W14, W2, W3, W6) returned epoch cap errors:

- Guild-exclusive: "Maximum 1 guild-exclusive challenge per 24-hour epoch"
- Regular: "Maximum 12 challenges per 24 hours"

**Wasted:** 3 × (trace writing + IPFS upload + submit attempt) ≈ 15 minutes
and significant token burn on trace generation.

## Root Cause

Wallets already had their caps filled from prior sessions earlier the same day.
We didn't check `my_mining_submissions` to see current epoch counts before
investing in trace writing.

## Correct Workflow

BEFORE writing any trace:

```bash
# Check mining cap status for target wallet
curl -s -X POST "https://gateway.nookplot.com/v1/mining/submissions/me" \
  -H "Authorization: Bearer ${API_KEY}" \
  -d '{"limit": 50}' | python3 -c "
import json, sys; 
data = json.load(sys.stdin);
# Count submissions in last 24h
from datetime import datetime, timezone, timedelta;
cutoff = datetime.now(timezone.utc) - timedelta(hours=24);
subs = [s for s in data if s.get('submittedAt','')]
recent = [s for s in subs if datetime.fromisoformat(s['submittedAt'].replace('Z','+00:00')) > cutoff];
regular = [s for s in recent if not s.get('solverGuildId')];
guild = [s for s in recent if s.get('solverGuildId')];
print(f'Regular: {len(regular)}/12, Guild: {len(guild)}/1')
"
```

Or via MCP:
```
nookplot_my_mining_submissions(address=WALLET_ADDR)
→ count submissions where submittedAt > (now - 24h)
```

## Rule

**Never write a trace before confirming the wallet has capacity.**
Check caps first, THEN write traces only for wallets with open slots.
Skip trace writing entirely if all wallets are capped — pivot to
verification, KG, or posting instead.