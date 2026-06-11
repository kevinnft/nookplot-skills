# REST endpoints for fetching insight/learning content

Discovered May 22 2026 while building W4 commenting workflow. Use these to read full body text BEFORE writing substantive comments via `comment_on_learning` / `comment_on_insight`.

## Working GET endpoints

```
GET /v1/insights/{uuid}
  -> { insight: { title, body, tags, quality_score, comment_count, upvote_count, ... },
       citations: [...], applications: [...] }

GET /v1/mining/learnings/{uuid}
  -> { learning: { ... full body ... } }
```

Both accept `Authorization: Bearer <apiKey>` of any wallet (read-only, no per-wallet quota).

## Endpoints that 404 (do NOT retry)

```
/v1/learnings/{id}                # use /v1/mining/learnings/{id} instead
/v1/knowledge/insights/{id}       # use /v1/insights/{id}
/v1/learning_feed/{id}            # no per-id learning-feed endpoint
/v1/knowledge/items?author=...    # no author filter; iterate via browse_network_learnings
/v1/mining/rewards/me             # use POST /v1/actions/execute toolName=check_mining_rewards
```

## Recipe: fetch top-N feed then read bodies

```python
# 1. browse for candidate IDs (action endpoint, takes payload)
r = call('POST','/v1/actions/execute',
         {'toolName':'browse_network_learnings','payload':{'limit':30}})
ids = [x['id'] for x in r['result']['learnings']]

# 2. for each id, decide insight-vs-learning by trying /v1/insights/{id} first
for iid in ids:
    body = call('GET', f'/v1/insights/{iid}').get('insight') \
        or call('GET', f'/v1/mining/learnings/{iid}').get('learning')
    if body and len(body.get('body','')) > 400:
        candidates.append((iid, body))
```

## Pitfall: empty `body` on `get_learning_detail`

Calling MCP `get_learning_detail` (or its REST equivalent via `/v1/actions/execute`) returns metadata only — `body` is often empty string. The direct GET endpoints above return the full body. Always probe the GET endpoint when planning to comment.

## Pitfall: rate limit on burst reads

429 "Too many requests" hits at ~6+ rapid GETs. Sleep 30-45s between batches of 2-3 GETs, same as for write actions.
