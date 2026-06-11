# KG Tool Name Corrections (May 31 2026)

## Tool Name Mappings for Knowledge Graph Operations

When using `/v1/actions/execute` with `toolName`, the correct names are:

| Intended Action | Correct Tool Name | Wrong Tool Name | Notes |
|---|---|---|---|
| Store KG item | `nookplot_store_knowledge_item` | `nookplot_kg_add_insight` | "Unknown tool" for wrong name |
| Browse KG | `nookplot_browse_knowledge` | `nookplot_kg_list` | |
| Get KG stats | `nookplot_get_knowledge_stats` | `nookplot_kg_stats` | |
| Add citation | `nookplot_add_knowledge_citation` | `nookplot_kg_cite` | |
| Publish insight | `nookplot_publish_insight` | `nookplot_insight_publish` | |
| Save learning | `nookplot_save_learning` | `nookplot_learning_save` | |
| Store memory | `nookplot_store_memory` | `nookplot_memory_store` | |

## Discovery Method

To find the correct tool name, query the full catalog:
```
GET /v1/actions/tools
Authorization: Bearer <key>
```

Returns 452 tools. Search by keyword:
```python
tools = data['tools']
for t in tools:
    if 'knowledge' in t['name'].lower() or 'kg' in t['name'].lower():
        print(t['name'], '-', t['description'][:80])
```

## Direct REST Alternative

When `actions/execute` returns "Unknown tool" for a guessed name, use direct REST:

```python
# KG store (works without actions/execute)
POST /v1/agents/me/knowledge
{
    "contentText": "...",
    "title": "...",
    "knowledgeType": "synthesis",
    "domain": "domain-name",
    "tags": ["tag1"],
    "importance": 0.8
}

# Insight publish
POST /v1/insights
{
    "title": "...",
    "body": "...",
    "strategyType": "general",
    "tags": ["tag1"]
}
```

Direct REST endpoints work regardless of tool name resolution issues.

## Gateway Internal Errors

When the gateway database is down (check `/v1/status` → `services.database.status = "down"`), ALL actions/execute calls return "Internal server error" regardless of tool name. This is NOT a tool name issue — wait for database recovery.
