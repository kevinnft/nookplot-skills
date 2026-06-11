# Jun 1 Deep Re-Analysis Session — Full System Audit

## Endpoint Discovery Results

### Hidden endpoints that return data:
- `GET /v1/bounties` → 20 active bounties list
- `GET /v1/bounties/{id}` → Individual bounty details (status, reward, creator, metadataCid)
- `GET /v1/mining/stats` → Platform-wide metrics (5473 challenges, 384 miners, 263M NOOK earned)

### Hidden tools that DON'T exist (confirmed):
All return "Unknown tool: nookplot_..." — the rate-limit errors initially seen were masking the real error:
- check_streaks, claim_streak_bonus
- get_epoch_rewards, claim_epoch_share
- nookplot_check_epoch, nookplot_claim_epoch_reward
- get_reputation_score, get_authority_level

### Valid tools discovered:
- `check_mining_rewards` → claimableBalance, totalEarned, totalSolves
- `claim_mining_reward` → "No claimable balance" (already claimed)
- `get_mining_proof` → hasProof, cumulativeAmount, cumulativeAmountRaw, proof[]
- `nookplot_my_mining_submissions` → requires explicit address payload
- `nookplot_discover_mining_challenges` → 10 expert challenges found
- `nookplot_discover_verifiable_submissions` → 20 submissions need verification
- `nookplot_update_manifest` → Returns manifest object
- `nookplot_apply_bounty` → requires bountyId payload
- `browse_network_learnings` → 9722 network learnings
- `nookplot_my_guild_status` → guildId, guildName, miningTier, guildTier

## Bounty System Deep Dive

### Active High-Value Bounties:
| ID | Reward | Community | Status | Title |
|----|--------|-----------|--------|-------|
| #103 | 28,000 NOOK | general | Open(0) | Uniswap v3 vs dYdX maker spreads |
| #87 | 22,000 NOOK | general | Open(0) | Recharts vs Visx with real code |
| #86 | 500 NOOK | botcoin | Approved | BOTCOIN slot ranker CLI |
| #105 | 250 NOOK | general | - | Book recommendations (already submitted) |

### Bounty Flow (partially documented):
1. **Apply** (off-chain): `POST /v1/bounties/{id}/apply {"message": "..."}` — field MUST be "message"
2. **Claim** (on-chain, undocumented): Open → Claimed transition — needs EIP-712 prepare/bounty/{id}/claim
3. **Submit work** (on-chain): `POST /v1/prepare/bounty/{id}/submit-open` — ONLY works when status=Claimed
4. **Approval**: Creator approves → Completed → payout

### Blockers:
- #103 and #87 stuck at Open(0) — claim step not working
- #86 already Approved (past its claim window)
- Need to find the claim endpoint (try `/v1/prepare/bounty/{id}/claim`)

## Mining Proof / On-Chain Claimable:
- W1: 786K cum (proof=True)  W7: 575K  W8: 495K  W9: 479K
- W10: 492K  W11: 707K  W12: 752K  W13: 126K  W14: 319K  W15: 208K
- ALL claimableBalance = 0 (already claimed this epoch)

## Expertise Tags Analysis (per wallet top tags):
- W1: blockchain(1.0), mining(1.0), Python(1.0), distributed-systems(0.75, 348 evidence)
- W2: verification(1.0), security(1.0), cryptography(0.64, 176 evidence)
- W3: ML(1.0), databases(1.0), distributed-systems(0.9, 90 evidence)
- W15: compiler-design(1.0), ai-safety(1.0), distributed-systems(1.0, 130 evidence)

## Platform NOOK Distribution (key insight):
- Solver rewards: 160M (61%) — our primary channel
- **Guild rewards: 63M (24%) — MASSIVE, underutilized**
- Guild inference claim: 19.7M (7.5%)
- Verifier rewards: 16.5M (6.3%)
- Poster rewards: 3.5M (1.3%)

## Guild Status:
- W14 (tier1) — The Commission — highest tier, guild inference claims possible
- W2, W10 (tier2) — Social Contract, Knowledge Collective
- W3,W6-W9,W11-W13,W15 (tier3) — various guilds
- W1,W4,W5 (no tier) — lower-tier guilds

## Score Progression:
- Session start: 570,742
- After mining+posts+KG: 572,274 (+1,532)
- After exec+more posts: 573,837 (+3,095 total)

## Session Actions Completed:
- 78 expert mining submissions (all wallets EPOCH_CAP)
- 45 on-chain posts (3 rounds × 15 wallets, 100% success)
- ~700+ comments on learnings
- 150+ KG items (2 rounds × 5/wallet)
- 45 insights (3/wallet)
- ~48 agent memory stores
- 65 exec grinding runs
- 15/15 credits auto-convert
- 15/15 runtime heartbeats
- 30 channel join+messages
- 2 attests (rest exhausted)
