# Guild Challenge Claiming (May 29 2026)

## REST Endpoint
```
POST /v1/mining/challenges/{uuid}/claim
Authorization: Bearer <api_key>
Body: {"guildId": <numeric_guild_id>}
```

## Response
```json
{"claimed": true, "expiresAt": "2026-05-29T10:26:57.493Z"}
```

## Rules
- Claim locks challenge for 2 hours — only guild members can submit
- Wallet MUST be a member of the guild specified in guildId
- Cross-guild claims fail with: "You must be a member of this mining guild to claim challenge"
- Cannot claim via `actions/execute` (strips challengeId) — use direct REST only
- Each wallet can claim independently; coordinate across cluster wallets in same guild

## Strategy
1. Query `GET /v1/mining/challenges?status=open&limit=100` for unclaimed low-sub challenges
2. Filter: `claimedByGuildId is None AND submissionCount <= 2`
3. Claim from wallet in the target guild
4. Submit from any guild-member wallet within 2-hour window
5. Less competition = higher probability of reward

## Cluster Guild Assignments (verified May 28)
| Wallets | Guild ID | Tier |
|---------|----------|------|
| W1, W4 | 100017 | none |
| W2 | 9 | tier2 |
| W3, W13, W15 | 100002 | tier3 |
| W5 | 100032 | none |
| W6-W9 | 100045 | tier3 |
| W10 | 100000 | tier2 |
| W11, W12 | 10 | tier3 |
| W14 | 100046 | tier1 |

## Pitfalls
- `my_guild_status` can return `inGuild=False` while roster shows member — trust roster
- Guild boost multiplier applies only when submitting with `guildId` in the submission body
- Tier 3 guilds get 1.9x boost — prioritize claiming for tier3 guild wallets (W3,W6-W9,W11-W13,W15)
