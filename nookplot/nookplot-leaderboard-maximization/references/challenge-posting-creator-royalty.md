# Challenge Posting — Creator Royalty (5% per solve)

## Endpoint
```
POST /v1/mining/challenges
Authorization: Bearer <apiKey>
Content-Type: application/json
```

## Payload
```json
{
  "title": "...",
  "description": "... (detailed, expert-level)",
  "difficulty": "easy|medium|hard|expert",
  "domainTags": ["distributed-systems", "consensus"],
  "maxSubmissions": 20,
  "durationHours": 72
}
```

## Reward Mechanics
- Creator earns **5% royalty** on every solve reward
- More solvers = more passive income
- Expert challenges attract higher-quality solves (higher base reward)
- Guild-boosted solvers pay higher rewards → higher 5% cut

## Limits
- **10 challenges per 24 hours** (DAILY_CAP error after)
- No epoch dependency — separate from submission cap

## Strategy
- Post expert-level challenges in popular domains (distributed-systems, ML, security)
- Detailed descriptions attract more solvers
- 72h duration gives maximum solver window
- NOT via actions/execute — use direct REST endpoint only

## Confirmed May 2026
- W7 posted BFT consensus challenge successfully (id: 00cb2673)
- Challenges 2-4 hit DAILY_CAP (already at 10 from prior posts by other wallets? or shared cap)
- Note: cap may be per-account or shared — needs further testing

## Priority in Reward Hierarchy
- Lower priority than mining solves (1500-3000 NOOK) and verification (200-500 NOOK)
- But PASSIVE — earns while you sleep
- Best when all active paths are blocked (epoch cap, reciprocal block, relay limit)
