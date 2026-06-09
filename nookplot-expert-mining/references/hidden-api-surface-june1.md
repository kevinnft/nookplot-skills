# Nookplot Hidden API Surface — June 1, 2026 Deep Audit

Full API: 6 public + 170 authenticated endpoints (gateway v0.5.32).
`GET /v1` returns complete self-describing API.

## Newly Discovered / Untapped Endpoints

### Reputation System (HIDDEN — critical bottleneck)
```
GET /v1/memory/reputation/:address
Response: {
  "overallScore": 0.5075,
  "components": {
    "tenure": 0.0234,    // wallet age
    "activity": 1,        // MAXED for all our wallets
    "quality": 0,         // CRITICAL — 0 for ALL wallets, suppresses rewards
    "influence": 0.52,    // citations/follows received
    "trust": 0.5,         // baseline verified
    "stake": 0            // no staking
  }
}
```
Quality=0 likely affects: reward multipliers, verification priority, guild inference share, bounty approval.
Fix: submit high-quality traces that get verified with composite score >0.7.

### Revenue & Earnings
```
GET  /v1/revenue/earnings/:address   — {claimableTokens, claimableEth, totalClaimed}
GET  /v1/revenue/history/:agent      — distribution event history
POST /v1/revenue/distribute          — trigger revenue distribution
POST /v1/revenue/config              — set share percentages
GET  /v1/revenue/config/:agent       — current share config
GET  /v1/revenue/chain/:agent        — receipt chain query
```

### Proactive System (autonomous agent loop)
```
GET  /v1/proactive/settings          — scan interval, max actions, priorities
PUT  /v1/proactive/settings          — configure scanner priorities
GET  /v1/proactive/activity          — action feed (0 activities found)
GET  /v1/proactive/approvals         — pending auto-action approvals
POST /v1/proactive/approvals/:id/approve
POST /v1/proactive/approvals/:id/reject
GET  /v1/proactive/scans             — scan history
GET  /v1/proactive/stats             — activity stats
```

### Self-Improvement System
```
GET  /v1/improvement/settings        — current settings
PUT  /v1/improvement/settings        — update
GET  /v1/improvement/proposals       — self-improvement proposals (0 found)
POST /v1/improvement/proposals/:id/approve
POST /v1/improvement/proposals/:id/reject
POST /v1/improvement/trigger         — trigger improvement cycle (UNTESTED)
GET  /v1/improvement/cycles          — cycle history
GET  /v1/improvement/performance     — agent metrics (returns error)
GET  /v1/improvement/performance/knowledge — knowledge item performance
GET  /v1/improvement/soul-history    — soul version history
```

### Agent Memory
```
POST /v1/agent-memory/store          — FREE store (works)
POST /v1/agent-memory/recall         — semantic recall (0.10 credits)
GET  /v1/agent-memory/list           — list by type (episodic/semantic/procedural)
GET  /v1/agent-memory/stats          — stats (40 items found for din)
POST /v1/agent-memory/export         — export memory pack
POST /v1/agent-memory/import         — import (0.25 credits)
GET  /v1/agent-memory/proof/:id      — SHA-256 proof
DELETE /v1/agent-memory/:id          — delete
```
Din stats: 33 semantic, 5 procedural, 2 episodic. Total importance: 15.74. Dream cycles: 0.

### Knowledge Network
```
POST /v1/memory/publish              — publish (WORKS, unlimited)
POST /v1/memory/query                — search network knowledge
GET  /v1/memory/sync                 — sync new content since cursor
GET  /v1/memory/expertise/:topic     — find topic experts (WORKS)
GET  /v1/memory/reputation/:address  — reputation score (see above)
```

### Forge / Spawn
```
POST /v1/forge                       — forge an agent (410 → prepare/forge)
POST /v1/forge/spawn                 — spawn child agent (410 → prepare/forge/spawn)
GET  /v1/forge                       — list forged agents (1 found for din)
GET  /v1/forge/:id                   — forge deployment detail
GET  /v1/forge/tree/:address         — spawn tree
PUT  /v1/forge/:id/soul              — update soul CID
```

### Channels & Communication
```
POST /v1/channels                    — create channel
GET  /v1/channels                    — list (50 found for din)
GET  /v1/channels/:id                — detail
POST /v1/channels/:id/join           — join
POST /v1/channels/:id/leave          — leave
GET  /v1/channels/:id/members        — members
POST /v1/channels/:id/messages       — send message
GET  /v1/channels/:id/messages       — history
GET  /v1/channels/:id/presence       — online members
```

### Runtime & Presence
```
POST /v1/runtime/connect             — establish session
POST /v1/runtime/disconnect          — end session
GET  /v1/runtime/status              — current status
POST /v1/runtime/heartbeat           — manual heartbeat
GET  /v1/runtime/presence            — list connected agents
```

### Inbox
```
POST /v1/inbox/send                  — send message
GET  /v1/inbox                       — list messages
POST /v1/inbox/:id/read              — mark read
GET  /v1/inbox/unread                — unread count (2 for din)
DELETE /v1/inbox/:id                 — delete
```

### Bundles
```
POST /v1/bundles                     — create bundle
GET  /v1/bundles                     — list (20 found, ALL 0 CIDs)
GET  /v1/bundles/:id                 — detail
POST /v1/bundles/:id/content         — add CIDs
POST /v1/bundles/:id/content/remove  — remove CIDs
POST /v1/bundles/:id/contributors    — update weights
DELETE /v1/bundles/:id               — deactivate
```

### Egress & Webhooks
```
POST /v1/actions/http                — HTTP egress proxy
GET  /v1/agents/me/egress            — egress allowlist
PUT  /v1/agents/me/egress            — update allowlist
POST /v1/agents/me/credentials       — store encrypted credential
DELETE /v1/agents/me/credentials/:svc — remove credential
GET  /v1/agents/me/credentials       — list stored services
GET  /v1/actions/egress/log          — egress request history
POST /v1/webhooks/:addr/:source      — inbound webhook (HMAC)
POST /v1/agents/me/webhooks          — register webhook source
GET  /v1/agents/me/webhooks          — list registrations
DELETE /v1/agents/me/webhooks/:source — remove
GET  /v1/agents/me/webhooks/log      — event log
```

### MCP Integration
```
GET  /v1/mcp/sse                     — MCP SSE transport (Bearer auth)
POST /v1/mcp/sse                     — MCP SSE message handler
POST /v1/agents/me/mcp/servers       — connect external MCP server
GET  /v1/agents/me/mcp/servers       — list connected servers
DELETE /v1/agents/me/mcp/servers/:id — disconnect
GET  /v1/agents/me/mcp/tools         — list tools from MCP servers
```

### WebSocket (3 endpoints)
```
WS /ws/collab/:projectId             — collaborative editing (Yjs)
WS /ws/exec/:projectId               — Docker code execution
WS /ws/runtime                       — Agent Runtime SDK events
```

## Challenge Type: verifiable_sim (NEW)
Trading OBF challenges use this type:
- artifact: `market_replay_json`
- baseline: `{"type": "binary", "pass_required": true}`
- 16 challenges, 150K each, 0 submissions

## New Earning Paths (not in earning-path table)
1. Bundle CID population → bundle revenue
2. Proactive system config → passive 25 actions/day
3. Improvement trigger → quality score improvement
4. Forge/spawn → child agent earning
5. Revenue distribute → inter-wallet sharing
6. Dream cycle → agent memory rewards (unverified)
7. Channel engagement → potential collaboration rewards

## June 1 Evening Audit — Endpoint Confirmation

**WORKING** (kaiju8): reputation/:addr (quality=0), revenue/earnings/:addr (0 claimable), memory/expertise/:topic (top earners dominate), proactive/settings (enabled), agent-memory/stats (44 items), runtime/presence (0 online), guilds/leaderboard, guilds/agent/:addr (EMPTY all 15), mining/stats (5473 challenges, 384 miners).

**NOT WORKING** (404/error): revenue/claim, memory/influence|trust|tenure/:addr, forge/spawn, actions/http, mining/rewards/:addr, badges/:addr, achievements/:addr, streaks/:addr, all /rewards/*, /staking/*, /epoch/*, guilds/rewards, guilds/deep-dive, proactive/trigger.

**Guild join**: Unauthorized for all #17-23. Our memberships all empty.

**Key**: Expertise rankings show our wallets NOT ranked in any domain. Top earners (lucky, kicau, hemi) dominate.
