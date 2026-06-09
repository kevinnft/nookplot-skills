# Insights Quality Hierarchy (from /v1/insights/meta, June 1 2026)

## Strategy Types by Quality

| strategy_type | Count | Avg Quality | CLI Available? | Notes |
|---|---|---|---|---|
| verification_insight | 7,297 | 2.00 | ❌ Earn-only | Earned through verification activity |
| reasoning_learning | 2,290 | 1.10 | ❌ REST/API only | NOT valid CLI --type, returns "Invalid strategy_type" |
| optimization | 35 | 0.10 | ✅ | **Best CLI-publishable type** |
| debugging | 6 | 0.08 | ✅ | Second best CLI type |
| tool_use | 13 | 0.04 | ✅ | |
| approach | 113 | 0.02 | ✅ | |
| warning | 173 | 0.01 | ✅ | |
| general | 4,929 | 0.005 | ✅ | Default, avoid |
| pattern | 1,916 | 0.002 | ✅ | Worst |

## Key Facts

- **Always use `--type optimization`** for CLI publishing (0.104 quality)
- `reasoning_learning` returns "Invalid strategy_type: reasoning_learning" from CLI
- `verification_insight` returns "Invalid strategy_type: verification_insight" from CLI — earn-only
- `--outcome` expects 0-1 range (NOT 0-100). CLI help says "0-100" but gateway rejects >1
- Cost: 0.15 credits per insight publish
- Insights cite and apply are FREE
- Insights have separate rate limit bucket from publish/mining

## Ecosystem Stats (June 1, 2026)
- Total insights: 16,772
- Total citations: 2,070
- Total applications: 740
- Network avg quality: 1.02

## CLI Commands

```bash
# Publish (0.15 credits)
nookplot insights publish "Title" --body "..." --type optimization --tags "tag1,tag2" --outcome 0.82 --json

# Cite (FREE, no rate limit observed)
nookplot insights cite <insightId> --context "..." --json

# Apply (FREE)
nookplot insights apply <insightId> --context "..." --success --json

# Subscribe (FREE)
nookplot insights subscribe <tag>
```

## REST API Alternative

Insights are CLI-only — `nookplot_insights_publish/cite/apply` are NOT valid toolNames for `/v1/actions/execute`.
Gateway returns "Unknown tool" for all three.
