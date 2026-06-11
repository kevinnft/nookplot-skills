# Dual-Wallet Mining Constraints (2026-05-16)

## Summary
Dual-wallet Nookplot mining is **not feasible** with current API coverage. MCP tools support only one wallet (configured in MCP server), and REST API lacks write endpoints.

## Tested Configuration
- **Wallet 1 (MCP)**: 0x5fcf1ae16aef6b4366a7af015c0075eba83ab030
  - Full functionality via MCP tools
  - Successfully completed 10 verifications, stored 5 knowledge items, posted 4 comments
  - Reputation: 32,353, pending earnings: 1,000-5,000 NOOK

- **Wallet 2 (REST)**: 0x5b82be8587b6e2680f4bbf86b987055b2604934c
  - Zero activity (blocked by API limitations)
  - Fresh account (0 reputation, 0 credits)

## REST API Coverage Gaps

### ✅ Working (Read Operations)
- `GET /v1/agents/me` - Agent profile
- `GET /v1/mining/profile` - Mining stats
- `GET /v1/mining/challenges` - List challenges
- `GET /v1/mining/submissions/pending-verification` - List submissions to verify

### ❌ Missing (Write Operations)
- `POST /v1/mining/challenges/{id}/submit-solution` - Returns 404 or GUILD_REQUIRED
- `POST /v1/knowledge/items` - Returns 404
- `POST /v1/insights/{id}/comments` - Returns 404
- `POST /v1/mining/submissions/{id}/verify` - No submissions available
- Guild operations - No endpoints exposed

## Blockers Discovered

### 1. Challenge Solving
- All non-guild challenges are `RLM_REPLAY` type (no handler live as of 2026-05-16)
- Guild-exclusive challenges require guild membership
- No REST endpoint for guild operations (join, claim, etc.)

### 2. Verification Mining
- 0 submissions available for verification at time of testing
- Verification endpoint exists but no work available

### 3. Social Engagement
- Comment endpoints return 404
- Insight/learning endpoints not available in REST API

### 4. Knowledge Mining
- Knowledge item storage endpoint returns 404
- No alternative write paths available

## Root Cause
1. **MCP tools**: Single-wallet only (configured in `~/.hermes/config.yaml` MCP server settings)
2. **REST API**: Read-only (write endpoints either missing or return 404)
3. **Guild operations**: Not exposed in REST API
4. **Challenge types**: Non-guild challenges use unimplemented verifier kinds

## Workarounds

### Option A: Configure Second MCP Server
Add a second MCP server entry in `~/.hermes/config.yaml` with wallet 2 credentials:
```yaml
mcp:
  servers:
    nookplot:
      command: npx
      args: ["-y", "@nousresearch/nookplot-mcp"]
      env:
        NOOKPLOT_API_KEY: "nk_wallet1_key"
    nookplot-wallet2:
      command: npx
      args: ["-y", "@nousresearch/nookplot-mcp"]
      env:
        NOOKPLOT_API_KEY: "nk_wallet2_key"
```
Then use `mcp_nookplot_wallet2_*` tools for wallet 2 operations.

### Option B: Wait for REST API Expansion
Monitor Nookplot gateway for new write endpoints. Current API is read-only by design or incomplete.

### Option C: Single-Wallet Strategy (Recommended)
Focus on maximizing wallet 1 earnings via MCP tools. Use wallet 2 later when:
- REST API write endpoints are added
- Second MCP server is configured
- Guild membership enables more challenges

## Earning Path Comparison

| Path | Wallet 1 (MCP) | Wallet 2 (REST) |
|------|----------------|-----------------|
| Challenge solving | ✅ Available (guild-dependent) | ❌ Blocked (no handler or guild) |
| Verification mining | ✅ 10 submitted | ❌ 0 available |
| Knowledge mining | ✅ 5 items stored | ❌ Endpoint 404 |
| Social engagement | ✅ 4 comments | ❌ Endpoint 404 |
| Guild operations | ✅ Via MCP | ❌ Not exposed |

## Recommendations

**Short-term (next session):**
1. Continue wallet 1 mining via MCP tools
2. Monitor verification quorum completion
3. Claim rewards when `claimableBalance > 0`
4. Join guild to unlock more challenges

**Medium-term (this week):**
1. Configure second MCP server for wallet 2
2. Build reputation on wallet 1 first
3. Use wallet 1 guild membership for wallet 2 (if guild allows multi-wallet)

**Long-term (strategic):**
1. Focus single-wallet strategy (wallet 1 via MCP)
2. Maximize wallet 1 earnings first
3. Use wallet 2 when API coverage improves
4. Consider wallet 2 for different domains/guilds to avoid rate limit conflicts

## Key Insight
Dual-wallet mining is currently **bottlenecked by API coverage**, not by rate limits or caps. MCP tools provide full functionality but only for one wallet. REST API is too limited for mining operations.

## Session Evidence
- Session: 2026-05-16 20:30-21:30 UTC
- Wallet 1 activity: 10 verifications (avg score 0.858), 5 knowledge items, 4 comments
- Wallet 2 activity: 0 (all write operations blocked)
- Full report: `/tmp/nookplot_dual_wallet_report.txt`
