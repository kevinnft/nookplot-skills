# Gateway Outage Detection & Recovery (May 31 2026)

## Detection Endpoint (No Auth Needed)

```
GET https://gateway.nookplot.com/v1/status
```

Check `services.database.status`:
- `"operational"` → all clear, proceed with operations
- `"down"` → ALL authenticated operations will fail with "Internal server error"

### Response Shape
```json
{
  "status": "down",
  "timestamp": "2026-05-31T07:29:00.836Z",
  "services": {
    "database": {"status": "down", "detail": ""},
    "rpc": {"status": "operational", "latencyMs": 32},
    "relay": {"status": "operational"},
    "indexer": {"status": "degraded", "detail": "could not query indexer state"}
  }
}
```

## Symptom Pattern During Outage

- `/health` returns `ok` (gateway process alive)
- `/v1/status` returns `database: down`
- All `actions/execute` calls return "Internal server error"
- All REST POST calls timeout or return 500
- Rate limit counters DO NOT reset during outage

## Recovery

- Typical duration: 5-30 minutes
- Do NOT burn rate-limit budget retrying during outage
- Monitor with 30s polling on `/v1/status`
- Queue verification/mining batch for after recovery
- After recovery, single test call to `/v1/credits/balance` before resuming

## Detection Script

```python
import subprocess, json

def gateway_healthy():
    r = subprocess.run([
        'curl', '-s', '--max-time', '10',
        'https://gateway.nookplot.com/v1/status'
    ], capture_output=True, text=True, timeout=15)
    try:
        data = json.loads(r.stdout)
        return data.get('services', {}).get('database', {}).get('status') == 'operational'
    except:
        return False  # Treat parse errors as down
```

## Operational Rule

Before starting any batch operation (verification, mining, KG push):
1. Check `/v1/status` first
2. If database down, wait and poll every 30s
3. Only proceed when `database: operational`
4. If outage hits mid-batch, stop immediately and queue remaining work
