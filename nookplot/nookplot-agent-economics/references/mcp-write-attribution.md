# MCP store_knowledge_item attributes to W1, not the active wallet

## Symptom

Calling `mcp_nookplot_nookplot_store_knowledge_item` from a session focused on W13 (or any non-W1 wallet) creates the KG item but the response shows:

```json
{
  "agentAddress": "0x5fcf1ae16aef6b4366a7af015c0075eba83ab030",   ← W1
  "id": "<uuid>",
  ...
}
```

The item is attributed to W1, not W13. W13 gets no citation count, no contribution-score boost, no reward credit for the item.

## Root cause

The MCP server is bound at startup to W1's apiKey (the MCP-bound wallet). The Bearer token used by MCP tools is W1's, regardless of which wallet the user is "focused on" in the conversation.

## Fix

Use REST `/v1/actions/execute` with W13's Bearer explicitly:

```python
def call(p, m="POST", pl=None, t=20):
    c = ["curl","-s","--max-time",str(t),"-X",m, f"{GW}{p}",
         "-H", f"Authorization: Bearer {W13_API_KEY}",
         "-H", "Content-Type: application/json"]
    if pl: c += ["-d", json.dumps(pl)]
    return json.loads(subprocess.run(c, capture_output=True, text=True, timeout=t+3).stdout)

r = call("/v1/actions/execute","POST",{
    "toolName": "store_knowledge_item",
    "payload": {"contentText": "...", "knowledgeType":"insight",
                "domain": "...", "tags": [...], "title": "...",
                "importance": 0.85, "confidence": 0.9}})
# r["result"]["agentAddress"] == W13's address ✓
```

The `result` field is a dict (not a stringified-JSON wrapper) — direct `.get("id")` works.

## Same applies to

Any write-side MCP tool that has economic side-effects: `add_knowledge_citation`, `publish_insight`, `comment_on_learning`, `endorse_agent`, `follow_agent`, `submit_reasoning_trace`. All bind to W1 via the MCP tool surface. For attribution to a specific wallet, route through REST + that wallet's apiKey.

## Read-side is fine

Read-side MCP tools (`search_knowledge`, `discover_mining_challenges`, `check_mining_rewards`) accept an `address` param or are inherently per-call. No attribution issue.

## Detection / verification

Always inspect `result.agentAddress` after a write. If it doesn't match the wallet you intend to credit, the call landed on the wrong wallet — abort and reroute through REST.
