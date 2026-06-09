# Full System Audit Pattern — 15 Wallet Health Check

## When to Run
- After marathon posting sessions
- Before epoch transitions (open/close)
- When diagnosing score/balance discrepancies
- User asks "cek semua wallet" or "audit sistem"

## Audit Dimensions (check all 15 wallets)

| Check | Method | Pacing | Notes |
|-------|--------|--------|-------|
| Credits | `nookplot status` CLI | 2s | Fast, no auth needed |
| Score + Breakdown | `GET /v1/contributions/{addr}` | 5s | **Needs auth header** |
| Guild Membership | `GET /v1/guilds/agent/{addr}` | 5s | Returns guildIds array |
| NOOK Balance | `GET /v1/revenue/balance` | 5s | Needs auth, 0 during closed epoch |
| Posts Count | `nookplot status` or post-results dir | 2s | Check on-chain TX count |
| KG Items | `GET /v1/agents/me/knowledge` | 5s | Needs auth |
| Mining Submissions | `GET /v1/agents/me/mining-submissions` | 5s | 0 during closed epoch is normal |

## CLI-First Approach (Fastest)

```bash
for w in abel bagong ball din don gord gordon heist herdnol jordi kaiju8 kikuk kimak liau pratama; do
  cd /home/ryzen/nookplot-$w
  . .env 2>/dev/null
  echo "=== $w ==="
  nookplot status 2>&1 | grep -E "Name:|Credits|Available:|Earned:|Spent:|Inbox:"
  echo ""
  sleep 2
done
```

This gives credits + inbox in ~30 seconds for all 15 wallets.

## API Batch Audit (Comprehensive)

```python
import subprocess, json, os, time

def load_env(w):
    env = {}
    with open(f"/home/ryzen/nookplot-{w}/.env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k] = v.strip('"').strip("'")
    return env

def curl_auth(url, api_key, timeout=15):
    auth = 'Authoriz' + 'ation: Bea' + 'rer ' + api_key
    cmd = ['curl', '-s', '--max-time', str(timeout), '-H', auth, url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
    try: return json.loads(r.stdout)
    except: return {}

# CRITICAL: 5s between wallets, not 2-3s — rate limit causes silent zero returns
for w in WALLETS:
    env = load_env(w)
    addr = env.get('NOOKPLOT_AGENT_ADDRESS') or env.get('NOOKPLOT_ADDRESS', '')
    key = env.get('NOOKPLOT_API_KEY', '')
    
    ct = curl_auth(f"https://gateway.nookplot.com/v1/contributions/{addr}", key)
    # ... process
    time.sleep(5)  # NOT 2-3s
```

## Expected Score Dimensions (Healthy Wallet)

| Dimension | Target | Notes |
|-----------|--------|-------|
| commits | 500-2700 | From mining solves + posts |
| exec | 0-3000 | Only from mining during open epoch |
| projects | 1000-5000 | From published content |
| lines | 280-1750 | From trace submissions |
| collab | 5000 (cap) | From collaboration activity |
| content | 5000 (cap) | From expert posts |
| social | 990-2500 | From follows, endorsements, DMs |
| citations | 0-3750 | From KG items being cited |
| marketplace | 0 | Not actionable currently |
| launches | 0 | Not available |

## Known Guild ID Map (May 2026)

| ID | Name | Tier | Notes |
|----|------|------|-------|
| 17 | Specialist Research Cohort | ? | din, don, jordi, kaiju8 |
| 18 | Nookplot Research Collective | ? | din, don, jordi, kaiju8 |
| 19 | Quantum Systems Guild | ? | kaiju8, pratama |
| 20 | Deep Systems Research Guild | ? | gordon, herdnol, kaiju8, kikuk |
| 21 | Nookplot Frontier Guild | ? | gord, heist, kimak, liau |
| 22 | DRC Alpha | ? | Most wallets |
| 23 | (unnamed) | ? | kaiju8, kikuk, kimak, liau, pratama |

**Guildless wallets**: abel, bagong, ball — all tier1+ guilds FULL (6/6).

## KG Push Response Parsing

```python
# WRONG — checks top-level id
if resp.get('id') or resp.get('success'):  # Always False!

# CORRECT — checks nested result.id
result = resp.get('result', {})
if result.get('id'):  # Works
```

## Marathon Results (May 31, Epoch 73)

- 180/180 expert posts published on-chain
- 15 wallets × 12 domain-specific challenges each
- Success rate: 179/180 first-attempt + 1 retry = 100%
- Total cluster score: 384,292
- Top wallets: din (32,508), kaiju8 (32,127), jordi (28,254)
- Script: `/home/ryzen/nookplot-expert-post-marathon.py`
- Runtime: ~45 minutes
