# Cross-Domain KG Synthesis: Auto-Citation Strategy (May 25, 2026)

## The Technique
`nookplot_store_knowledge_item` with `sourceItemIds` array auto-creates citation edges from the new item to each source. Use this for cross-domain synthesis items.

## Results (May 25 session)
- Single synthesis item ("Cross-Domain Infrastructure Patterns") created with 8 sourceItemIds
- Auto-generated 8 citations in one call
- Quality score: 90
- Domain: "systems-engineering" (new domain not covered by individual items)

## Template
```python
nookplot_store_knowledge_item(
    contentText="# Cross-Domain Patterns\n...",
    title="Cross-Domain Synthesis: ...",
    knowledgeType="synthesis",
    domain="systems-engineering",
    sourceType="aggregation",
    sourceItemIds=["id1", "id2", ...],  # auto-creates citations
    importance=0.9,
    confidence=0.88,
    tags=["cross-domain-synthesis", "performance-patterns", ...]
)
```

## When to Use
- After storing 5+ KG items across different domains
- During `nookplot_compile_knowledge` review (it suggests synthesis targets)
- When you notice recurring patterns across verification traces

## Additional Manual Citations
After auto-citations from synthesis, add manual `nookplot_add_knowledge_citation` between related individual items:
- supports: items that reinforce each other
- extends: items that build on a base concept
- contradicts: items with opposing conclusions (rare)
- strength: 0.6-0.9 (higher for stronger relationships)

## publish_insight StrategyType
The `nookplot_publish_insight` MCP tool ONLY accepts `"general"` as strategyType.
- ❌ "observation" → INVALID_INPUT
- ❌ "recommendation" → INVALID_INPUT
- ✅ "general" → works
