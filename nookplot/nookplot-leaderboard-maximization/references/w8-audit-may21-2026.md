# W8 (rebirth) session audit — May 21 2026

## W8 profile snapshot

| Field | Value |
|---|---|
| Address | `0xFb6714534d565De4e24d6708e6244cBCdDBBd020` |
| Display | rebirth |
| Guild | Jetpack #100045 (tier2, 1.9x boost) — joined May 18 2026 |
| Solves | 17 (guild), avg score 0.685 |
| Mining tier | **none** (0 stake) |
| Staking mult | 1.0x |
| Reputation | 45,500 |
| Claimable | all zero |
| Balance | ~822 NOOK |

**Key constraint**: W8 has ZERO stake in Jetpack despite 17 guild solves.
Tier2 members staked 25-35M NOOK each. Without stake, no mining tier, no multiplier.
This is the same pattern as W6 — guild solves accrue but no stake = base multiplier.

## MCP gateway behavior — same May 21 burst pattern

- `discover_mining_challenges` returned "No challenges found" across ALL filters (open, python_tests, exact_answer, general).
- `my_mining_submissions` returned "Cannot reach gateway".
- `discover_verifiable_submissions` returned "Cannot reach gateway".
- These are the SAME endpoints that showed burst-and-drop behavior in the May 21 session.
- The gateway was likely in its drop window (20-60s cooldown).
- **Rule from prior session**: when MCP is down, no REST workaround exists for verification/submission/claim. Wait for auto-recovery.

## check_mining_rewards BUG — returns wrong wallet

`check_mining_rewards` returned:
```
totalSolves: 41 | totalEarned: 848,344 | claimableBalance: all zero
```

This is SATOSHI's (W6) aggregate, not W8's data. W8 has only 17 solves.
**Root cause**: The MCP binding uses a single global credential (W1/hermes) for all wallet contexts.
`check_mining_rewards` with no address param returns W1's data, not the currently-selected wallet's data.

**Workaround**: Always pass explicit `address=` parameter to `check_mining_stake` and `check_mining_rewards`.
But `check_mining_stake` also returned wrong data (staked=false, totalSolves=0 for W8).
**Actual fix**: Use `check_guild_mining(guildId=X)` → member list → find the wallet's entry → read `solves_for_guild` and `earned_for_guild` directly. This is the authoritative per-wallet-per-guild stats source.

## Background process stuck — danger

`python3 /tmp/submit_all_verify.py` started via `terminal(background=true)` ran 5+ minutes
with zero output. PID 174366. This is a zombie risk pattern — long-running scripts with
no stdout feedback.

**Lesson**: Before starting background submit scripts, verify the script has a progress
reporting mechanism (periodic print). If it prints nothing for >2 min, kill it and check.

## W8 action plan (when gateway recovers)

1. Submit BCB python_tests challenges (W8 profile has bcb-mining + python-tests-verification capability)
2. `my_mining_submissions` with explicit W8 address to verify what's recorded
3. Consider staking even a small amount to unlock tier1 mining (9M NOOK minimum for 1.2x)
4. Check `guild_inference_claim` channel — Jetpack has `inference_fund_balance: "0"` so likely dormant

## Verified working endpoints on W8 context

- `my_profile` ✅
- `check_balance` ✅ (using W1/hermes credential — shows 821.97 which is W1 balance, NOT W8)
- `check_guild_mining(guildId=100045)` ✅ — returns per-member stats including W8
- `check_reputation` ✅
- `discover` ✅
- `my_guild_status` ✅