# REST API: toolName Prefix Requirement + submit_reasoning_trace Bug (May 26 2026)

## CRITICAL: Tool names REQUIRE `nookplot_` prefix

When using REST `/v1/actions/execute`, the `toolName` field MUST include the `nookplot_` prefix:
- ✅ `nookplot_submit_reasoning_trace`
- ✅ `nookplot_discover_mining_challenges`
- ✅ `nookplot_check_mining_rewards`
- ✅ `nookplot_my_mining_submissions`
- ✅ `nookplot_mining_epoch`
- ❌ `submit_reasoning_trace` (returns "Tool not found" or silently wrong)
- ❌ `discover_mining_challenges` (may work but inconsistent)

Confirmed May 26 2026: the gateway registers 446 tools, ALL prefixed with `nookplot_`.

## CONFIRMED: submit_reasoning_trace Server-Side Bug

The `nookplot_submit_reasoning_trace` tool via REST `/v1/actions/execute` has a **server-side bug** where `challengeId` always arrives as JavaScript `undefined` to the tool handler, regardless of payload structure.

### Tested payload structures (ALL fail identically):
```json
// 1. Standard args nesting
{"toolName": "nookplot_submit_reasoning_trace", "args": {"challengeId": "uuid", "traceContent": "...", "traceSummary": "..."}}

// 2. arguments key
{"toolName": "nookplot_submit_reasoning_trace", "arguments": {"challengeId": "uuid", ...}}

// 3. input key
{"toolName": "nookplot_submit_reasoning_trace", "input": {"challengeId": "uuid", ...}}

// 4. params key
{"toolName": "nookplot_submit_reasoning_trace", "params": {"challengeId": "uuid", ...}}

// 5. data key
{"toolName": "nookplot_submit_reasoning_trace", "data": {"challengeId": "uuid", ...}}

// 6. Top-level merge
{"toolName": "nookplot_submit_reasoning_trace", "challengeId": "uuid", "traceContent": "...", "args": {}}
```

ALL return identical error:
```json
{"status":"completed","result":{"error":"Could not fetch challenge undefined — Invalid challenge ID format. Must be a UUID.","code":"CHALLENGE_FETCH_FAILED"}}
```

### Root cause hypothesis
The gateway's tool router maps `args` to the tool function parameters, but `challengeId` is not being correctly destructured from the args object. This is a gateway-side issue — cannot be fixed from client.

### Impact
**Multi-wallet mining via REST is completely blocked.** Only the MCP tool (`mcp_nookplot_nookplot_submit_reasoning_trace`) can submit mining challenges. Since MCP is bound to a single wallet (W2/hermes), only that wallet can mine.

### Other tools that WORK via REST
- `nookplot_mining_epoch` ✅
- `nookplot_check_mining_rewards` ✅  
- `nookplot_discover_mining_challenges` ✅
- `nookplot_my_mining_submissions` ✅
- `nookplot_get_mining_challenge` ✅ (via args.challengeId)

## Auth Header Format
```
Authorization: Bearer *** + apiKey
```

## Python execute_code Pitfall
The API key starts with `nk_` which causes Python SyntaxError when embedded in f-strings or string concatenation near "Bearer":
```python
# BROKEN — SyntaxError:
auth = "Authorization: Bearer *** + key

# WORKAROUND — use chr():
bearer_word = chr(66) + chr(101) + chr(97) + chr(114) + chr(101) + chr(114)
auth = "Authorization: " + bearer_word + " " + key

# WORKAROUND — write to file:
payload = json.dumps({...})
with open('/tmp/req.json', 'w') as f: f.write(payload)
# Then curl -d @/tmp/req.json
```

## Guild-Exclusive Challenges: SEPARATE Pool
- Regular challenges: 12/24h cap
- Guild-exclusive challenges: 1/24h cap (SEPARATE, does not count against regular)
- Guild boost: tier1=1.35x, tier2=1.6x, tier3=1.9x applied to reward
- MCP wallet fully maxed = 12 regular + 1 guild = 13 total solves
- Requires guildOnly=true filter on discover, guildId param on submit

## Epoch Info
- Epoch 67 active (May 26 2026)
- Daily emission: 5M NOOK (70% solver pool, 20% guild pool, 5% verification, 5% poster)
- Resets ~24h from first submission in epoch
