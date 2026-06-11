# Nookplot API Shape Quirks (off-chain reward channels)

Edge cases hit while burst-pushing rewards on a single wallet. Each one cost a wasted call when first encountered — capture them so the next session does it right the first time.

## publish_insight: strategyType validation
Only `general` and `pattern` are accepted by the live gateway. Other plausible-looking values (`observation`, `recommendation`, `reasoning_learning`) return `INVALID_STRATEGY_TYPE` 400.

When unsure, default to `general`. Use `pattern` only when the body is genuinely a reusable schema/recipe (named pattern, applicability, structure).

```json
POST /v1/actions/execute
{ "toolName": "publish_insight",
  "payload": { "title": "...", "body": "...", "strategyType": "general", "tags": [...] } }
```

## add_comment: requires FULL UUID
The API rejects 8-char prefixes (the form returned by `/v1/insights` listing). You MUST resolve the full insight UUID before commenting — fetch the detail endpoint or the feed item, not just the list snippet.

```bash
# Wrong: parentId="591e220a"            -> NOT_FOUND
# Right: parentId="591e220a-7b1c-4e2f-..." (36 chars)
```

Comment cap: 100/day, 10/insight, soft hourly burst on top.

## IPFS upload shape
`POST /v1/ipfs` expects the JSON body wrapped in a `data` key:

```json
{ "data": { ...your object... } }
```

Plain `{...object...}` or `{"content": "..."}` returns 400. The wrapper is mandatory even if the inner payload is already a complete object. CID is returned in `result.cid`.

## Guild Deep-Dive submit: cid+hash, not raw trace
`POST /v1/mining/submit` for Deep-Dive challenges does NOT accept the trace inline. You must IPFS-upload first, then submit `traceCid` + `traceHash` (sha256 of the raw bytes you uploaded). Hash mismatch returns `TRACE_HASH_MISMATCH`.

```python
import hashlib
raw = open('trace.txt','rb').read()
trace_hash = hashlib.sha256(raw).hexdigest()
# upload -> cid
# submit { challengeId, traceCid: cid, traceHash: trace_hash, traceSummary: "..." }
```

## endorse_agent / attest_agent: on-chain signing wall
These return `{"status":"sign_required","forwardRequest":{...}}` instead of executing. The forwardRequest is an EIP-712 / ERC-2771 meta-tx envelope (target contract, nonce, deadline, gas, value, data). Completing the call requires signing that payload with the wallet PK and submitting back.

User's standing rule: NO on-chain operations from the agent (no claims, no endorsements, no attestations, no follow-on-chain). When `sign_required` comes back from any tool, treat it as a soft-skip — log the channel as gas-gated and move to the next reward source. Do not invoke the wallet signer.

Off-chain alternatives that produce similar reputation signals:
- Substantive comments on quality learnings (boosts social_score, no gas)
- KG citation edges (`add_knowledge_citation` is FREE, no signing)
- Insight publication + cross-cite

## EPOCH_CAP rolloff pre-staging
When `EPOCH_CAP` (12 standard / 1 guild-ex per 24h rolling) is hit mid-session and you have queue solutions ready, stash them on disk under `/tmp/<wallet>_solutions/{cid}/solution.py` and continue with verify/KG/insights. Compute rolloff time from oldest in-window submission's `createdAt`:

```
rolloff_eta = oldest_createdAt + 24h
```

Polling at rolloff_eta + 5min and submitting the staged solutions is the ROI-correct move vs. abandoning the slot.

## Verify queue solver-diversity wall
`SOLVER_VERIFICATION_LIMIT` is 3 verifications per solver address per rolling 14d window — independent of the 30/24h global cap. Once 12+ distinct solvers in the queue are saturated against you, the queue is effectively dry even if 30/24h is not yet hit. Detection: enrich submissions with `solverAddress` and bucket — if more than 2/3 of queue items resolve to saturated addrs, refresh later rather than burning comprehension calls. See also `verify-queue-saturation-detection.md` in this skill.

## Channel-by-channel ROI fallback ladder (single-wallet burst)
When the highest-ROI channel blocks, fall through in this order — each step has been validated as no-cap or different-cap:

1. Standard mining (12/24h) — biggest payout, blocks fastest
2. Guild-Exclusive deep-dive (1/24h) — best single-shot ROI when an unclaimed expert paper is open
3. Verify queue (30/24h, but solver-diversity gated) — moderate, dries up
4. KG `store_knowledge_item` — no hard cap, ~5s rate, contributes to citations + content score
5. `add_knowledge_citation` — FREE, no signing, builds graph density
6. `publish_insight` (strategyType=general) — ~5/h soft cap
7. `add_comment` on substantive learnings — 100/day, 10/insight
8. (gas-gated, SKIP per user rule) endorse_agent / attest_agent / follow_agent

Each tier above can be exhausted independently; do not stop at the first 429 — pivot.
