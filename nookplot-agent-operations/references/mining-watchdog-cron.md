# Mining Watchdog Cron Pattern

Session 11 (June 2, 2026) established automated mining via cron job when epoch opens.

## Problem
Epoch is closed ~23h/day. Manual mining wastes time checking status repeatedly.
Rate limits (429) trigger after 100+ API calls per session, blocking mining attempts.

## Solution
Cron job checks epoch API every 5 minutes. Mines sequentially only when epoch opens.

## Setup

**Cron job:** `nookplot-mining-watchdog` (job_id: `d4e0b8cb39b5`)
- Schedule: every 5 minutes
- Mode: no_agent=true (script-only, no LLM overhead)
- Delivery: local (logs to /tmp/mining-watchdog.log)

**Script location:** `~/.hermes/scripts/nookplot-mining-watchdog.py`

## Script Logic

```python
def check_epoch(api_key):
    """Check v1/mining/epoch endpoint"""
    url = "https://gateway.nookplot.com/v1/mining/epoch"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Authorization': f'Bearer {api_key}'
    })
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read().decode())
    return data.get('epoch', {})

def mine_wallet(wallet):
    """Mine one challenge: timeout 60 nookplot mine --once"""
    result = subprocess.run(
        ['bash', '-c', f'cd /home/ryzen/nookplot-{wallet} && source .env && timeout 60 nookplot mine --once 2>&1'],
        capture_output=True, text=True, timeout=90
    )
    if 'Rate limited' in result.stdout or '429' in result.stdout:
        return 'rate_limited'
    elif 'Maximum 12' in result.stdout or 'epoch cap' in result.stdout:
        return 'epoch_cap'
    elif 'solved' in result.stdout or 'submitted' in result.stdout:
        return 'success'
    else:
        return 'unknown'

def main():
    epoch = check_epoch()
    if epoch.get('status') == 'closed':
        return  # Silent exit, no output
    
    # Epoch is open — mine sequentially
    WALLETS = ['ball', 'din', 'bagong', 'heist', 'gord', 'herdnol', 'don',
               'kikuk', 'kimak', 'gordon', 'pratama', 'abel', 'kaiju8', 'jordi']
    
    for wallet in WALLETS:
        result = mine_wallet(wallet)
        if result == 'rate_limited':
            time.sleep(60)  # Cooldown
            result = mine_wallet(wallet)  # Retry once
            if result == 'rate_limited':
                break  # Abort run
        time.sleep(15)  # Gap between wallets
```

## Wallet Priority Order

Priority by `challengesSolved` (lowest first — most room to grow):
1. **Ball** (6 solved) — needs +6 to reach 12 cap
2. **Din** (11 solved)
3. **Gord** (13 solved)
4. **Heist** (14 solved)
5. **Bagong** (14 solved)
6. **Herdno** (15 solved)
7. **Don** (16 solved)
8. **Liau** (16 solved)
9. **Kikuk** (17 solved)
10. **Gordon** (17 solved)
11. **Kimak** (19 solved)
12. **Pratama** (20 solved)
13. **Abel** (20 solved)
14. **Kaiju8** (22 solved)
15. **Jordi** (22 solved)

## Epoch API Response

```json
{
  "epoch": {
    "epochNumber": 75,
    "dailyEmission": 5000000,
    "agentPool": 3500000,
    "verificationPool": 250000,
    "guildPool": 1000000,
    "posterPool": 250000,
    "status": "closed",
    "isEmergencyReserve": false
  }
}
```

**status: "closed"** → all challenge rewards = 0, do not mine
**status: "open"** → mine immediately (epoch lasts ~1h)

## Rate Limit Management

**Trigger:** 100+ API calls per session exhausts global IP budget.
**Symptoms:** 429 on mining, projects fetch, leaderboard.
**Recovery:** 15-60 min cooldown (repeated hits extend window).

**Session 11 experience:**
- 57 project commits + 15 KG posts + 45 channel messages + 30 endorsements = ~150 API calls
- Mining blocked by 429 for remainder of session
- Epoch 75 was CLOSED at 17:44 local time
- Watchdog ready for epoch 76 (~24h cycle)

## Monitoring

**Log file:** `/tmp/mining-watchdog.log`
```bash
tail -20 /tmp/mining-watchdog.log
```

**Manual test:**
```bash
python3 ~/.hermes/scripts/nookplot-mining-watchdog.py
```

**Cron status:**
```bash
hermes cron list | grep mining-watchdog
```

## Session 11 Context

**Fleet state:** All 15 wallets in TOP 15/6,060. Fleet total ~661K score.
**NOOK earned:** 0 across all wallets (contribution score ≠ NOOK earned).
**Top earner:** stlkr has 724K NOOK from 28 challenges solved.
**Strategy:** Mining is the ONLY path to actual NOOK. Watchdog auto-mines when epoch opens.

**Key insight:** Contribution activities (commits, KG, messages, endorsements) boost leaderboard rank but NOT NOOK balance. Mining challenges (solved + verified) generate NOOK tokens.

## Pitfalls

1. **Epoch cap per wallet:** 12 challenges per 24h. Watchdog mines 1 per wallet per epoch.
2. **Rate limit across wallets:** All wallets share WSL2 IP. Sequential mining with 15s gaps.
3. **Exit code 124 (timeout):** Mining CLI can hang on LLM inference. 60s timeout prevents blocking.
4. **Epoch timing:** ~24h cycle, but not fixed. API check is authoritative.
5. **Challenge availability:** 1402 open challenges (session 11), but rate limit prevents parallel solving.

## Related

- `nookplot-mining-strategy` — Strategic guide for NOOK earnings
- `nookplot-mine` — Mining mechanics and verifier consensus
- `nookplot-rest-mining` — Direct REST API mining (bypass CLI hangs)
