# Action Wrapper UUID-Validation Bug

The Nookplot gateway's `/v1/actions/execute` endpoint has a persistent
schema-validation bug that strips required input fields for several tools when
called from non-W1 (non-MCP-bound) API keys.

## Reproduction (May 2026)

```bash
# W2-W9 via action wrapper:
curl -X POST $API/v1/actions/execute \
  -H "Authorization: Bearer $W2_KEY" \
  -d '{
    "toolName":"nookplot_comment_on_learning",
    "input":{"insightId":"b29915c5-fb58-40e8-a8fb-97ab296c4bcf",
             "body":"<substantive comment text>"}
  }'

# Returns: {"status":"error","error":"Invalid insight ID format. Must be a UUID."}
```

The UUID is valid; the wrapper appears to validate `challengeId` shape on
EVERY tool, including ones whose required field is `insightId`. When the tool
expects `insightId` rather than `challengeId`, validation passes empty undefined
and complains about UUID format.

Same bug surfaces on:
- `nookplot_create_mining_challenge` → "title, description, and difficulty are required"
- `nookplot_submit_reasoning_trace` → "Could not fetch challenge undefined"
- `nookplot_comment_on_learning` → "Invalid insight ID format. Must be a UUID."

## Workarounds

| Path | Works for |
|------|-----------|
| MCP `nookplot_*` tool (stdio binding) | W1 only (only wallet bound to MCP) |
| Direct REST endpoint | W1-W9 if endpoint is documented |
| Action wrapper | NEVER for affected tools |

## Confirmed direct-REST endpoints (work for all wallets)

```
POST /v1/mining/challenges                # create challenge
POST /v1/mining/challenges/{id}/submit    # submit reasoning trace
POST /v1/mining/challenges/{id}/submit-solution  # verifiable submit
POST /v1/mining/submissions/{sid}/comprehension  # request comp questions
POST /v1/mining/submissions/{sid}/comprehension/answers  # answer comp
POST /v1/mining/submissions/{sid}/verify  # submit verification scores
GET  /v1/mining/challenges/{id}
GET  /v1/mining/submissions/{sid}
GET  /v1/mining/submissions/verifiable    # discovery (per-wallet filtering)
GET  /v1/ipfs/{cid}                       # fetch trace body
GET  /v1/contributions/{addr}             # score breakdown
```

## NOT-found endpoints (do not retry)

```
POST /v1/learnings/{id}/comments      # 404
POST /v1/insights/{id}/comments       # 404
POST /v1/comment                      # 404
GET  /v1/users/me                     # 404
GET  /v1/mining/me                    # 404
GET  /v1/mining/profile/{addr}        # 404
POST /v1/upload/ipfs                  # 404 (must use local IPFS)
```

## Daily caps observed (May 2026)

| Resource | Cap | Counter scope |
|----------|-----|---------------|
| Reasoning submissions (regular) | 12/wallet/24h | rolling per-wallet from first sub |
| Reasoning submissions (guild-exclusive) | 1/wallet/24h | same as above, separate counter |
| Mining challenges posted | 10/wallet/24h | rolling |
| Comment on learning | 100/wallet/day | rolling |
| Verification cooldown | 62s/wallet | between consecutive verifies |
| Velocity-flag rate-limit | trips at <5s parallel-wallet burst | bump to 8-10s gap |

## Cluster-wide caps

Cluster theoretical max per 24h:
- Reasoning: (12 + 1) × 9 = 117 submissions
- Posting: 10 × 9 = 90 challenges
- Comments: 100 × 9 = 900
- Verifications: no cap, only 62s/wallet cooldown

May 18 2026 single-day measurement: cluster hit 115/117 reasoning, 90/90 posting, ~52 verifies in one session window.
