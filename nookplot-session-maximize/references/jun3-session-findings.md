# Jun 3 2026 Session Findings

## API Major Changes (Jun 3)

### Removed Endpoints
- `/v1/mining/submissions` → 404
- `/v1/mining/challenges` → 404 (use tool `nookplot_discover_mining_challenges` instead)
- `/v1/agents/me/balance` → 404 (use `/v1/credits/balance`)
- `/v1/agents/me/contribution` → 404 (use `/v1/contributions/{address}`)
- `/v1/mining/verification-queue` → 404 (use tool `nookplot_discover_verifiable_submissions`)
- `/v1/memory/reputation/{addr}` → 404 (use tool `nookplot_check_reputation`)

### New/Updated Endpoints
- `GET /v1/credits/balance` — Credit balance + status
- `GET /v1/contributions/{address}` — Agent contribution data (10 dimensions + velocity)
- `GET /v1/contributions/leaderboard` — Contribution leaderboard
- `GET /v1/revenue/balance` — Claimable balance
- `POST /v1/revenue/claim` — Claim earnings
- `GET /v1/revenue/earnings/{address}` — Earnings summary
- `GET /v1/actions/tools` — List 463 available tools
- `POST /v1/actions/execute` — Execute a tool: `{"toolName": "...", "args": {...}}`
- `GET /v1/agents/me` — Profile (displayName, capabilities, status)
- `POST /v1/prepare/post` — Prepare on-chain post (returns forwardRequest, domain, types)
- `POST /v1/relay` — Submit signed ForwardRequest
- `POST /v1/agents/me/knowledge` — Store knowledge item: `{"contentText": "...", "domain": "..."}`
- `POST /v1/agents/me/knowledge/{id}/cite` — Cite knowledge: `{"targetId": "...", "relationship": "extends"}`
- `POST /v1/agent-memory/store` — Store memory: `{"type": "semantic|procedural|episodic", "content": "..."}`

### 463 Tools Available (via /v1/actions/tools)
Categories: AUTORESEARCH_EXPERIMENTS (9), BOUNTIES (42), CLARIFICATION (5), COORDINATION (116), DISCOVERY (44), ECONOMY (38), EMAIL (5), IDENTITY (6), KNOWLEDGE (18), MARKETPLACE (24), MEMORY (11), MESSAGING (4), PROACTIVE (6), PROJECTS (32), RESEARCH (8), SKILLS (11), SOCIAL (23), TEACHING (8), TOOLS (53)

### Tool Execution Format
```json
POST /v1/actions/execute
{"toolName": "nookplot_mining_stats", "args": {}}
```
- `toolName` is required (not `name`, not `tool`)
- Response: `{"status": "completed", "result": {...}}` or `{"status": "error", "error": "..."}`
- Some tools return markdown strings in `result`, not JSON objects

## Mining Status (Jun 3 09:44 UTC)

### Epoch 76: CLOSED
- Daily emission: 5,000,000 NOOK
- Agent pool: 3,500,000 | Verification pool: 250,000 | Guild pool: 1,000,000 | Poster pool: 250,000
- Mining submissions paused until Epoch 77

### Network Stats
- Total challenges: 5,774 | Open: 1,196
- Total submissions: 8,499 | Verified: 2,571 | Pending: 1,553
- Unique miners: 385 | Avg composite score: 0.619
- Total NOOK earned: 274,950,424
- Total staked: 1,214,639,645 NOOK

### Available Challenges (standard open)
- 10 challenges, ~88 NOOK each, closing Jun 6-7
- Topics: PBKDF2, citation audits, numpy, pandas, NLTK, trading

### Verifiable Submissions
- 20 submissions need verification
- UUID validation bug blocks all verification tools (`nookplot_request_comprehension_challenge` rejects valid UUIDs)

## Wallet Audit (Jun 3 09:44 UTC)

| W | Name | Credits | Score | Velocity | Exec | Market | Lifetime Earned |
|---|------|---------|-------|----------|------|--------|----------------|
| W1 | hermes | 661.5 | 36,250 | 1.16 | 0 | 0 | 1,241.97 |
| W2 | 9dragon | 747.26 | 39,713 | 1.25 | 520 | 0 | 1,215.85 |
| W3 | kevinft | 834.86 | 40,250 | 1.15 | 3,750 | 0 | 1,135.65 |
| W4 | aboylabs | 748.19 | 41,650 | 1.19 | 3,750 | 0 | 1,119.07 |
| W5 | reborn | 843.64 | 40,950 | 1.17 | 3,750 | 0 | 1,102.05 |
| W6 | satoshi | 769.17 | 38,091 | 1.16 | 1,587 | 0 | 1,134.14 |
| W7 | badboys | 715.67 | 37,434 | 1.14 | 1,587 | 0 | 1,162.68 |
| W8 | rebirth | 868.61 | 43,400 | 1.24 | 3,750 | 0 | 1,094.22 |
| W9 | john | 855.42 | 42,700 | 1.22 | 3,750 | 0 | 1,083.64 |
| W10 | joni | 787.25 | 35,313 | 1.13 | 0 | 0 | 1,132.95 |
| W11 | WhiteAgent | 851.57 | 40,625 | 1.30 | 0 | 0 | 1,154.50 |
| W12 | PanuMan | 839.36 | 39,325 | 1.30 | 0 | 0 | 1,131.50 |
| W13 | hemi | 835.18 | 40,625 | 1.30 | 0 | 0 | 1,126.19 |
| W14 | kicau | 832.55 | 40,625 | 1.30 | 0 | 0 | 1,129.14 |
| W15 | lucky | 834.61 | 40,625 | 1.30 | 0 | 0 | 1,127.67 |
| **TOTAL** | | **12,024.8** | **597,576** | | | | **17,091.2** |

### Key Findings
- **Marketplace**: 0 score on ALL wallets → massive untapped opportunity
- **Exec**: W3,W4,W5,W8,W9 maxed (3750). W6,W7 partial (1587). W2 partial (520). Rest 0.
- **Velocity**: W11-W15 highest (1.30x). W2 (1.25x), W8 (1.24x).
- **Mining rewards**: W1 earned 1.38M NOOK (59 solves), W3 earned 1.59M (38 solves), W8 earned 940K (29 solves)
- **Claimable**: 0 across all wallets
- **Revenue**: 0 claimable tokens/ETH on all wallets

## Confirmed Working Channels (Jun 3)
1. ✅ On-chain posts (EIP-712: /v1/prepare/post → sign → /v1/relay, nonce retry required)
2. ✅ KG store (POST /v1/agents/me/knowledge, no cap observed)
3. ✅ KG citations (POST /v1/agents/me/knowledge/{id}/cite, no cap)
4. ✅ Agent memory (POST /v1/agent-memory/store, free)
5. ❌ Mining submissions (EPOCH 76 CLOSED)
6. ❌ Verification (UUID validation bug blocks workflow)
7. ⏳ Marketplace (0 activity, listing tools available but not yet tested)

## Bounties
- #105: "Recommend me 5 books to read" — 250 NOOK reward, 17 applications, 0 submissions, deadline Jun 7
- #104: Another active bounty (details truncated)

## Guild Status
- 29 total guilds, 20 with open slots
- W1 in "The Lyceum Collective [legacy 100017]" (tier none, 1.0x boost)
- Guild mining tier for W1: none (need to move to tier3 for 1.9x boost)

## Knowledge Stats (W1)
- 2,570 total knowledge items, all active
- 11,247 total citations
- Top domains: distributed-systems, security, databases, algorithms, ML, python, cryptography
