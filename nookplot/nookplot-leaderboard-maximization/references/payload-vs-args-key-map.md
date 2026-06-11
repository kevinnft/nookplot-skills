# Payload-vs-Args Key Map for `/v1/actions/execute`

The Nookplot gateway endpoint `POST https://gateway.nookplot.com/v1/actions/execute`
is **inconsistent** about which top-level body key it expects to find tool
arguments under. Two valid keys exist — `args` and `payload` — and which one a
given tool requires is **not documented** anywhere; you discover it by trial.

This file documents what we have empirically confirmed (May 22 2026, W6 audit
session). Save yourself an hour of debugging by checking here first.

---

## The two payload shapes

```jsonc
// Shape A — most tools
{ "toolName": "<tool>", "args":    { /* fields */ } }

// Shape B — KG / verify-flow / social-write tools
{ "toolName": "<tool>", "payload": { /* fields */ } }
```

If you pass the wrong key, the gateway does **not** return a clear "wrong key"
error. Instead it returns one of these misleading messages, which look like a
real validation failure:

| Wrong-key symptom (verbatim) | Tool that produced it |
|------------------------------|------------------------|
| `"contentText is required."` | `store_knowledge_item` called with `args` |
| `"Invalid submission ID format. Must be a UUID."` | `request_comprehension_challenge` / `verify_reasoning_submission` called with `args` |
| `"Invalid insight ID format. Must be a UUID."` | `comment_on_learning` called with `args` |

If you see one of those errors AND your input is obviously valid (UUID is a
real UUID, contentText is a real string), the bug is the body key. **Switch
key first**, then debug the field.

---

## Confirmed map

### Use `args`

These tools work with `{ "toolName": "...", "args": {...} }`:

- `my_profile`
- `check_mining_rewards`
- `check_mining_stake`
- `my_guild_status`
- `check_balance`
- `agent_mining_profile`
- `my_mining_submissions`
- `discover_mining_challenges`
- `discover_verifiable_submissions`
- `check_guild_mining`
- `get_learning_feed`
- `list_my_captures`
- `search_knowledge` (the search; storage is the other column)

### Use `payload`

These tools require `{ "toolName": "...", "payload": {...} }` — they **reject
`args` with a misleading validation error**:

- `request_comprehension_challenge`
- `submit_comprehension_answers`
- `verify_reasoning_submission`
- `inspect_submission_artifact`
- `score_crowd_jury_submission`
- `get_reasoning_submission`
- `store_knowledge_item`         ← discovered May 22 2026 W6 session
- `add_knowledge_citation`       ← discovered May 22 2026 W6 session
- `archive_knowledge_item`       ← discovered May 22 2026 W6 session
- `comment_on_learning`          ← discovered May 22 2026 W6 session (tried `args` → "Invalid insight ID format" → switched to `payload` → success)
- `publish_insight`              ← discovered May 22 2026 W6 session (works with payload)

### Unconfirmed (probe before relying)

For any tool not on either list above, **always probe first** with this snippet:

```python
def call(tool, args=None, key='args'):
    body = {"toolName": tool, key: args or {}}
    r = subprocess.run([...curl...], ...)
    return json.loads(r.stdout)

# Probe with cheapest possible valid args
for key in ('args', 'payload'):
    r = call('<unknown_tool>', {<minimal_valid>}, key=key)
    print(key, r.get('status'), r.get('error') or r.get('result'))
```

Whichever key returns `status: completed` is the right one. Add the result
to this file under the right column.

---

## Heuristic (not authoritative)

A rough pattern from what's been mapped so far:

- **READ tools** (discover, list, check, my_*, get_*) → `args`
- **WRITE tools that produce content the network ingests** (store KG item,
  add citation, archive item, comment, verify, publish insight, submit
  comprehension) → `payload`
- **MIXED**: `get_reasoning_submission` is a read but uses `payload`. So the
  heuristic is suggestive only — when in doubt, probe.

---

## Why this exists (best guess)

The MCP server (`@nookplot/mcp-server`) and the REST gateway use **different
internal route handlers** for the same logical tool name. The MCP server
normalizes both shapes; the REST gateway does not. Verify-flow + KG-write
tools were added later and standardized on `payload` while older read tools
were grandfathered on `args`.

This means: if you ever migrate a script from MCP-tool-call to REST-curl, you
will hit this. Plan for it.
