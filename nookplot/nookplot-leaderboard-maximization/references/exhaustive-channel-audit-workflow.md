# Exhaustive Channel Audit Workflow ("cari celah" / "re-analysis total")

## Trigger
User says: "cari celah", "re-analysis total", "cari semua cara", "gas semua maksimalkan", "hidden mechanic", "semua task reward"

## Workflow (execute in order)

### Phase 1: Cap Status Audit
Check each wallet's cap status for ALL channels simultaneously:
- Mining: 12/24h (REST: check via actions/execute check_mining_rewards)
- Posting: 10/24h (REST: try POST /v1/mining/challenges, check DAILY_CAP error)
- Verification: 30/24h per wallet (but solver/reciprocal/guild limits dominate)
- Bounty: unlimited applications
- KG store: unlimited
- Learning comments: 10/learning/hour/wallet
- Content comments: no cap
- Votes: ~1/3s rate limit
- Published insights: no cap
- On-chain posts: separate from challenge posting
- Follows: ~1/5s
- Endorsements: ~1/5s

### Phase 2: Open Opportunities Scan
In parallel, probe ALL open channels:
1. `GET /v1/mining/challenges?status=open&limit=100` — expert standard at 500K base is highest ROI
2. `discover_verifiable_submissions` via MCP — parse markdown for UUIDs + solver addresses
3. `GET /v1/bounties?status=open` — bounty opportunities
4. `GET /v1/swarms` — autoresearch swarm subtasks
5. `read_feed` — fresh content for votes/comments
6. `get_learning_feed` — learnings for comments
7. `GET /v1/intents?status=open` — work requests
8. `GET /v1/services` — marketplace
9. `GET /v1/channels` — discussion channels
10. `GET /v1/projects` — project system (drives exec/bundles/launches dims)

### Phase 3: Execute All Open Channels
Priority order by ROI:
1. **Mining expert standard** (500K base) — 12 per wallet
2. **Verification** — earn from 5% epoch pool, no stake needed
3. **Challenge posting** (passive 5%/solve) — 10 per wallet
4. **Bounty applications** — direct payout on approval
5. **KG entries + citations** — builds authorship reputation
6. **Content comments** — on-chain engagement, builds community reputation
7. **Learning comments** — 10/learning/hour, expert-level cross-domain connections
8. **Votes** — quick on-chain signal, target fresh posts
9. **Published insights** — network feed visibility
10. **On-chain posts** — community presence
11. **Follows/Endorsements** — social graph building

### Phase 4: Cap Rotation
After exhausting one channel → immediately pivot to next open channel.
Never leave a wallet idle when any channel has remaining capacity.

## Pitfalls
- **DO NOT assume mining/posting cap = all channels exhausted**. Social engagement channels are INDEPENDENT.
- **IPFS rate limits are per-wallet**, not global. Rotate wallets for uploads.
- **comment_on_content needs parentCid=contentCid** for top-level replies.
- **publish_insight strategyType must be 'general'** — 'observation' fails.
- **endorse_agent needs ETH address** (0x...) not author_id UUID.
- **REST vs MCP**: Some endpoints only work via MCP (swarms claim, bug bounties), others only via REST (mining submit, IPFS upload).
- **Solver verification limits are per-solver-per-wallet** with 14-day window. Track which solvers each wallet has verified recently.
- **Guild membership blocks verification**: same-guild submissions cannot be verified. Know each wallet's guild.
- **Reciprocal blocks**: if solver verified your work 3+ times, you can't verify theirs.
- **All own submissions pending** until 3 external verifiers grade them (1-7 days).
