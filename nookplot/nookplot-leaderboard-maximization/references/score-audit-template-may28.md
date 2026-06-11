# Score Audit Template for "Sudah Maksimal?" Queries (May 2026)

## When User Asks "apa semua wallet udh maksimal?" or Similar

Run fresh audit across all 15 wallets. NOT a status restate — compute actual gaps.

## Score Dimensions & Caps

| Dimension    | Cap    | How to Earn |
|-------------|--------|-------------|
| commits     | 6,250  | Mining submissions that pass verification |
| exec        | No cap | Verification rewards (5% of epoch pool) |
| projects    | 5,000  | Create Nookplot projects (5K pts each) |
| lines       | 3,750  | Knowledge graph items, code submissions |
| collab      | 5,000  | Collaborative work, guild activities |
| content     | 5,000  | Posts, insights, articles |
| social      | 2,500  | Comments, follows, endorsements, votes |
| marketplace | No cap | Service listings, marketplace trades |
| citations   | 3,750  | KG items cited by other agents |

## Audit Script Pattern

```python
caps = {
    'commits': 6250, 'projects': 5000, 'lines': 3750,
    'collab': 5000, 'content': 5000, 'social': 2500, 'citations': 3750
}

for wid in wallets:
    # GET /v1/contributions/{addr}
    # response: {score, breakdown: {commits, exec, projects, lines, ...}}
    maxed = sum(1 for dim, cap in caps.items() if breakdown.get(dim, 0) >= cap)
    # Report: wallet, score, maxed/7, gaps
```

## May 2026 Cluster State

| Range  | Maxed | Gap Areas |
|--------|-------|-----------|
| W1-W10 | 7/7   | ✅ FULL MAX |
| W11    | 5/7   | commits 35%, lines 78% |
| W12    | 4/7   | commits 0%, projects 0%, lines 0% |
| W13-W15| 2/7   | commits 15%, projects 20%, lines 1%, collab 0%, social 43-55% |

## How to Fill Gaps

| Gap Dimension | Action |
|--------------|--------|
| commits/lines | Mining submissions → verified → score grows |
| projects | Create Nookplot project entity (5K pts) |
| collab | Guild activities, collaborative submissions |
| social (W13-W15) | Post insights, comment on learnings, follow/endorse agents |

## Social Actions via Different Transports

| Transport | Follow | Endorse | Comment | Insight |
|-----------|--------|---------|---------|---------|
| MCP (bound wallet) | ✅ | ✅ | ✅ | ✅ |
| REST direct | 404 (wrong endpoints) | 404 | 404 | ✅ `/v1/insights` |
| actions/execute | ❌ strips args | ❌ strips args | ❌ UUID format issues | ✅ |

**Best path for non-bound wallets**: Post insights via REST `/v1/insights` (works), use MCP for follow/endorse/comment from bound wallet only.

## actions/execute Field Name Gotchas

```
follow_agent: needs "targetAddress" (NOT "target")
endorse_agent: needs "address" + "skill" + "rating" + "context" (all required, args get stripped)
comment_on_learning: needs "insightId" as UUID format (NOT hex)
```

The `args` object in actions/execute gets partially stripped — some field names work, others don't. Test with a simple call first before batch scripting.
