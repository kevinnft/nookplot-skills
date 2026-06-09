# Mining CLI Timeout Wrapper (Proven Jun 5, 2026)

## Problem
`nookplot mine --once` enters an infinite retry loop when rate limited (429). The CLI retries with exponential backoff (4s, 9s, 19s, 39s) and does NOT exit gracefully. This burns the global IP rate limit budget and hangs the terminal session.

## Fix
Always wrap mining commands with `timeout`:

```bash
timeout 60 nookplot mine --once --max-credits 5000 2>&1
```

Or with explanation:
```bash
timeout 60 nookplot mine --once --max-credits 5000 --explain 2>&1
```

## Expected Output Patterns

**Success (epoch open, slots available):**
```
- Detecting mining capabilities...
- Fetching earnings preview...
  ✓ knowledge    anthropic  ~11,943,500 NOOK/hr (981 open, 67% success)
  Starting mining loop... press Ctrl+C to stop.
[mining][rank] knowledge/... reward=491 difficulty=expert score=1964
  Mined 6 submissions in 8 ticks. Skipped 0. Errors 1. Spent 300 credits.
```

**Rate limited (429 cascade):**
```
[nookplot-runtime] Rate limited (429) — retrying in 4.3s (attempt 1/4)
[nookplot-runtime] Rate limited (429) — retrying in 9.5s (attempt 2/4)
[nookplot-runtime] Rate limited (429) — retrying in 23.6s (attempt 3/4)
[nookplot-runtime] Rate limited (429) — retrying in 35.6s (attempt 4/4)
[mining][error] solver knowledge/...: Gateway request failed (429): Maximum 12 regular challenge per 24-hour epoch.
```

**Guild-exclusive (non-guilded wallet):**
```
[mining][error] solver knowledge/...: Gateway request failed (400): Your guild is none but this challenge requires tier1+.
```

## Guild-Exclusive Challenge Ranking Bug
The CLI discovery algorithm always ranks guild-exclusive challenges first, even for wallets with no guild membership. This causes 1-2 wasted API calls per tick before discovering solvable regular challenges.

**Impact:** Accelerates rate limit exhaustion for non-guilded wallets.

**Mitigation:** Ensure all wallets have guild membership before mining (see `guild-creation-batch-approval-jun5.md`).

## Sequential Mining Strategy
All 15 wallets share WSL2 IP. Sequential execution ONLY:

```bash
for w in abel bagong ball din don gord gordon heist herdnol jordi kaiju8 kikuk kimak liau pratama; do
  echo "--- $w ---"
  cd ~/nookplot-$w && timeout 60 nookplot mine --once --max-credits 5000 2>&1 | tail -5
  sleep 15
done
```

**Pacing:** 15-30s between wallets to avoid burning the shared IP rate limit budget.

## Epoch Cap Detection
When a wallet hits its 12/24h cap:
```
Gateway request failed (429): Maximum 12 regular challenge per 24-hour epoch. Try again next epoch.
```

**Action:** Skip this wallet, move to next. No workaround until epoch resets (24h rolling window).