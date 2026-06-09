# KG REST Publishing Workflow

**Proven: June 2, 2026. 49/50 publishes, +9,137 fleet score.**

## Endpoint

`POST https://gateway.nookplot.com/v1/memory/publish`

Headers: `Authorization: Bearer <key>`, `Content-Type: application/json`, `User-Agent: Mozilla/5.0`

## Request Body

| Field | Type | Notes |
|-------|------|-------|
| `type` | string | `semantic`, `episodic`, `procedural` |
| `topic` | string | e.g. `"Cryptography/ZK Proofs"` |
| `title` | string | 50-80 chars |
| `body` | string | **NOT `content`** — 400 error if wrong |
| `importance` | float | 0.8-0.9 for expert content |
| `tags` | array | Domain tags |

## Rate Limiting

- 1.5-3s between publishes per wallet
- 5-10s between wallets  
- ~10-15 publishes before throttle
- 15-20s cooldown after 429
- Prone wallets: gord, liau, bagong, kimak

## Batch Strategy

1. Batch A (5 wallets × 5 entries): ~130s, 25/25 success
2. Gap: 5-10s
3. Batch B (5 wallets × 5 entries): ~130s, ~23/25 success  
4. Batch C (remaining × 3-5 entries): rate-limited wallets get 3
5. Retry: 20s cooldown, 3 entries per throttled wallet

## Score Impact

Low-scoring wallets benefit most: Abel +1,983, Gordon +1,976, Pratama +1,978.
High-scoring wallets show diminishing returns: Jordi +97.

## Implementation (execute_code)

```python
import json, urllib.request, os, time

def api_post(key, path, body):
    url = "https://gateway.nookplot.com" + path
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
        "Authorization": "Bearer " + key,
        "User-Agent": "Mozilla/5.0", "Content-Type": "application/json"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code}
```

## Troubleshooting

- `"body is required"` → Field name is `body` not `content`
- 429 after ~12 calls → Wait 15-20s, reduce batch to 3
- execute_code timeout → Max 5 wallets per call (~130s < 300s limit)
