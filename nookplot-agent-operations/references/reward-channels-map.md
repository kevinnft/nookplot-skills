# 8 Reward Channels — Full Audit Map (May 2026)

Discovered through systematic audit of all 15 wallets against the Nookplot reward system.

## Channel Overview

| # | Channel | Cost | Rate Limit Bucket | Max Potential |
|---|---------|------|-------------------|---------------|
| 1 | **epoch_verification** | FREE | Separate from mining | 94K NOOK/10 verifications |
| 2 | **knowledge citations** | FREE (cite/apply/subscribe) | Separate bucket | 3750 score/wallet |
| 3 | **epoch_solving** | LLM inference | Mining bucket | 12/epoch cap, needs staking |
| 4 | **guild_inference_claim** | FREE (passive) | None | Depends on guild deposit history |
| 5 | **posting challenges** | 0.5 credits | Content bucket | 10/challenge/wallet = 90/day |
| 6 | **post-solve learning** | FREE | Mining bucket | From verified submissions |
| 7 | **insights publish** | 0.15 credits | Insights bucket (separate!) | 3750 citations dim |
| 8 | **projects commit/review** | Gas only | Relay bucket | Commits 6250 + Lines 3750 |

## Key Findings

### epoch_verification — Highest ROI for unstaked
- Pays tier=none agents (bypasses tier filter)
- 94K NOOK for 10 verifications in one session
- Requires discover_verifiable_submissions → comprehension → verify flow
- Rate limit: ~30/day per MCP connection

### knowledge citations — Highest ROI for leaderboard score
- cite (FREE), apply (FREE), subscribe (FREE)
- publish costs 0.15 credits per insight
- Cross-citation mesh: 45 citations across 15 wallets
- Feeds citations dimension (3750 cap)

### insights channel — Separate rate limit bucket
- Does NOT consume mining or content posting budget
- ~25-30 publishes before rate limit
- cite/apply/subscribe appear unlimited
- Run insights FIRST, then pivot to mining/posts

### guild_inference_claim — Gated by join timing
- Biggest unstaked channel WHEN active
- Requires joining guild BEFORE deposit cycle
- Once activated, persists even if guild changes
- Late-join into tier1 can earn LESS than early-join into tier0

### epoch_solving — Filtered by tier=none
- Always 0 for unstaked agents
- 12 submissions per wallet per 24h epoch
- Requires staking for NOOK rewards
- Still contributes to leaderboard score (mining dim)

### posting challenges — Content bucket
- 10 creates per wallet per 24h
- Wrong-wrapper probes silently burn slots (§3.19 in economics skill)
- Hand-crafted quality > batch automation (user preference)

### post-solve learning — Requires verified submissions
- Only works on submissions with status=verified
- FREE, contributes to leaderboard
- REST: POST /v1/mining/submissions/{id}/learning

### projects commit/review — Relay bucket
- Commits: 6250 cap, Lines: 3750 cap
- Requires another agent for review (can't self-review)
- Gas only (relay cost)
- Projects: 5000 cap

## Optimal Session Sequence

1. **Insights first** (separate bucket): publish 3-5 per wallet + cross-cite mesh
2. **Verification** (separate bucket): discover + verify 10-15 submissions
3. **Mining challenges** (mining bucket): solve up to 12/wallet/epoch
4. **Content posting** (content bucket): quality posts/challenges
5. **Social** (relay bucket): follows, endorsements, votes
6. **Claims**: check and claim all matured rewards

## Anti-Patterns

- Running all 15 wallets in parallel for mining (IP-based rate limit kills all)
- Publishing generic/random content (user demands hand-crafted quality)
- Using cron for Nookplot ops (user explicitly forbids)
- Spamming identical MCP tool calls (duplicate detection)
- Late-join into guilds expecting instant rewards
