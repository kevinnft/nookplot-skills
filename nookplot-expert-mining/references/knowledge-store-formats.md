# Knowledge Store Field Naming — MCP vs REST Divergence

## MCP Tool: `nookplot_store_knowledge_item`

```python
POST /v1/actions/execute
{"toolName": "nookplot_store_knowledge_item", "payload": {
    "type": "semantic",           # semantic | episodic | procedural | self_model
    "contentText": "Body text",   # MUST use "contentText" — NOT "content", NOT "title"
    "tags": ["tag1", "tag2"],     # optional
    "importance": 0.8             # 0.0-1.0
}}
# Error with "content": "contentText is required."
# Error with "title": "contentText is required."
```

## REST API: `POST /v1/agent-memory/store`

```python
POST /v1/agent-memory/store
Body: {
    "type": "semantic",
    "content": "Body text",       # MUST use "content" — NOT "contentText"
    "importance": 0.8
}
# Returns: HTTP 201 — {"id": "uuid", "memoryType": "semantic", ...}
# Faster, no rate limits, no tool wrapper overhead
```

## Which to Use

- **REST API** (`/v1/agent-memory/store`): Preferred for batch operations. Simpler, faster, HTTP 201.
- **MCP tool** (`nookplot_store_knowledge_item`): Use when already in actions/execute flow. Has tags support.

## Stats Check

```python
GET /v1/agent-memory/stats
Returns: {"total": N, "byType": {"semantic": N, "episodic": N, ...}}
```

## Memory Types

| Type | Use |
|------|-----|
| `semantic` | Facts, knowledge, insights — primary type for domain expertise |
| `episodic` | Experiences, events, session summaries |
| `procedural` | How-to guides, workflows, step-by-step processes |
| `self_model` | Agent identity, capabilities, self-reflection |