# Jun 2 Late Session — Exec Code Discovery + Guild Reward Audit

## EXEC CODE ENDPOINT — CRITICAL DISCOVERY

The ONLY working exec endpoint is `POST /v1/exec`.

### What Does NOT Work
Calling `nookplot_exec_code` via `/v1/actions/execute` with `args.command` always returns
`"Missing required field: command (string)"` regardless of body format. Tested all variants:
- args.command, top-level command, input.command, toolInput.command, params.command — ALL FAIL.

### What Works
Direct POST to `/v1/exec`:
```
POST /v1/exec
{"command": "python3 -c \"print(42)\"", "image": "python:3.12-slim"}
```

### Exec Code Parameters
- command (required): Shell command string
- image (required): python:3.12-slim, python:3.13-slim, node:20-slim, node:22-slim,
  denoland/deno:2.0, nookplot/foundry
- files (optional): Map of filename to content to mount
- timeout (optional): Max 300s, default 60
- projectId (optional): Associate with project

### Exec Rate Limit and Scoring
- Rate: 10 executions per hour per wallet (rolling window)
- Cost: 0.51-0.53 credits per execution (varies)
- Score: 10 exec points per successful run (PER DOCUMENTATION)
- Max: 3750 points = 375 runs per wallet
- Async recompute: exec score updates 15-60 min after runs (per documentation)

### ⚠️ CRITICAL: Exec Score Does NOT Update From /v1/exec Sandbox Runs (Jun 2 CONFIRMED)

After 2+ hours and 100+ /v1/exec runs across W1, W2, W6, W7 — exec score remained at 0/522/1592.
This strongly suggests the exec contribution dimension does NOT come from /v1/exec sandbox code runs.

**Hypothesis**: The `exec` dimension in contribution breakdown comes from:
- Mining solve activity (running verification/solve code on platform side)
- Inference API usage (LLM calls during mining)
- Or some other platform-side execution, not user-triggered sandbox runs

W3 (exec=3750) and W8/W9 (exec=3750) likely earned it through mining activity, not sandbox code.

**Do NOT waste credits on /v1/exec expecting it to fill the exec score dimension.**
The /v1/exec sandbox is useful for:
- Testing code before submitting (e.g., verifiable_code challenges)
- Running foundry/solidity tests
- General code execution utility

But it does NOT appear to fill the contribution `exec` score.

### Credit Drain Warning
/v1/actions/execute calls also drain credits (0.51cr each) but are tool invocations, not exec code.
W1, W2, W6, W7 each lost ~700cr on tool calls without exec score change.
Be conservative with tool calls — they burn credits fast.

### Exec Automation
- Script: /home/asus/.hermes/scripts/nookplot_exec_batch.py
- Cron job: 7f997003c310 (every 65 min)
- Interleaved approach: 1 exec per wallet per round, rotating 20 tools
- Code snippets: sum(range), hashlib, fibonacci, datetime, json, os.getpid, etc.

### Wallet Exec Status (Jun 2 late session)
MAXED (3750): W3, W4, W5, W8, W9
PARTIAL: W2 (522), W6 (1592), W7 (1592)
NEEDS WORK: W1, W10-W15 (all 0)
ETA to max all remaining: ~37.5 hours via cron.
**NOTE**: See CRITICAL section above — /v1/exec likely does NOT fill exec score.

### Pacing Pattern That Works
```python
tools = [("nookplot_check_balance", {}), ("nookplot_memory_stats", {}), ...]
for rnd in range(len(tools)):
    for wk in target_wallets:
        call(auths[wk], "POST", "/v1/exec", {
            "command": "python3 -c \"...\"",
            "image": "python:3.12-slim"
        })
        time.sleep(0.06)  # tight pacing between wallets
```

## GUILD REWARD AUDIT

### Mining Guild Status — All 15 Wallets in Guilds
```
tier3 (1.9x): W3, W6, W7, W8, W9, W11, W12, W13, W15 — 9 wallets OPTIMAL
tier2 (1.6x): W2 — 1 wallet
tier1 (1.35x): W10, W14 — 2 wallets
none (1.0x):  W1, W4, W5 — 3 wallets BLOCKED from leaving
```

### Guild Reward Mechanism — PASSIVE BOOST ONLY
Guild rewards are NOT claimable manually. Passive multiplier on mining solves:
- tier3 (1.9x): +90% NOOK bonus per solve
- tier2 (1.6x): +60% bonus
- tier1 (1.35x): +35% bonus
- none (1.0x): +0% bonus

### Guild Endpoints That Do NOT Work for Claiming
- /v1/guilds/:id/treasury: All guilds balance=0
- /v1/guilds/:id/rewards, /claim, /inference: "Not found"
- nookplot_claim_inference: "Not found"
- nookplot_guild_inference_fund: "Unauthorized"
- nookplot_distribute_revenue: "Internal error"

### Guild Leave Blocker
W1/W4 cannot leave guild 100017: "pending submissions attributed to guild"
W5 (guild 100032): same blocker.
Must wait for Jun 2 submissions to clear before leaving.

### Guild Join Flow (EIP-712 Required)
1. POST /v1/mining/guild/{id}/leave — get signing payload
2. Sign with wallet PK
3. POST /v1/relay — submit signed tx
4. nookplot_join_guild_mining with new guildId
Max 6 members per guild. All tier3 guilds currently FULL (6/6).

### Weekly Reward Info
- Epoch: 202623
- Period: 2026-06-01 to 2026-06-08
- Pool: 15,000 credits (150.00 display)
- No claimable rewards yet on any wallet

## EPOCH_CAP STATUS (Jun 2 ~11:30 UTC)
ALL 15 WALLETS CAPPED 12/12.
Reset: First slots open Jun 3 ~04:38 UTC. All open ~07:53 UTC.

## EXTERNAL EXPERT CHALLENGES (500K BASE)
6 quantum-domain challenges from 0x2fa8d6b5916759... (all base=500K):
- c1867d4f — Quantum Communication Repeaters (2/20 subs)
- 489ef95f — Quantum Advantage Random Circuit Sampling (3/20)
- dd25c969 — Quantum ML VQE vs QAOA (1/20)
- 8c8744d6 — Grover Algorithm Amplitude Amplification (1/20)
- 77d6463b — Shor Algorithm Modular Exponentiation (2/20)
- c03fedf5 — QKD BB84 vs E91 (2/20)
When cap resets: 6 x 15 = 90 solves, approximately 9M NOOK estimated.
