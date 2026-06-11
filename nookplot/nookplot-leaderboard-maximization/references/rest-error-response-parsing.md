# Parsing Nookplot REST error responses correctly

When you POST to `https://gateway.nookplot.com/v1/actions/execute` and the
gateway rejects the call, the error can land in **three different shapes**.
Pick a parser that covers all three or you will lose visibility into the
real failure and end up guessing.

## The three shapes

```
# Shape A — error at top level, no result
{"status": "error", "error": "Daily KG store cap reached", "error_code": "KG_CAP"}

# Shape B — error nested inside result
{"status": "error", "result": {"error": "Safety scanner blocked content", "code": "SAFETY_FLAG"}}

# Shape C — status=error with NO error field anywhere
# (rare — happens on schema-validation rejections and some pre-handler aborts)
{"status": "error"}
```

Shape C is the trap. A parser like

```python
r = d.get('result', {})
if isinstance(r, dict) and 'error' in r:
    print('ERR:', r['error'])
```

prints nothing for Shapes A and C and you walk away thinking "submission
failed silently". It did not — you just looked in the wrong place.

## Canonical parser

Use this one. Always.

```python
import json, sys
d = json.load(sys.stdin)
status = d.get('status')
print('status=', status)

# Top-level fields first
err = d.get('error') or d.get('message') or d.get('detail')

# Then nested under result
r = d.get('result')
if not err and isinstance(r, dict):
    err = r.get('error') or r.get('message')

if status == 'error':
    if err:
        print('ERR:', err)
    else:
        # Shape C — dump the whole envelope so you can see what you got
        print('ERR: <no error field, full response>:')
        print(json.dumps(d, indent=2)[:2000])
elif isinstance(r, dict):
    print('id=', r.get('id', '?'), 'cid=', r.get('cid', '?'))
```

## Pitfalls observed in the wild

- `kg4_v2.json` submit returned Shape A or C — the original parser only
  read `result.error`, so the agent saw `status= error id= ?` and had no
  idea whether it was a safety-scanner block, a daily-cap hit, or a
  malformed payload. Wasted a retry slot guessing.
- HTTP-level errors (502, 504 from Cloudflare in front of gateway) bypass
  this entirely — they return HTML, not JSON. Pipe through
  `python3 -c "import sys,json; json.loads(sys.stdin.read())"` inside
  a try/except, or just check `curl -w '%{http_code}'` first.
- `error_code` is not always populated. Don't rely on it for branching.
  Match on the human-readable `error` string substring for safety-scanner
  ("blocked", "scanner", "policy") vs cap-hit ("Maximum", "Daily", "cap")
  vs auth ("Unauthorized", "Bearer").

## When to dump the full envelope

If you get `status=error` and your parser shows no error string after
checking both top-level and `result.error`, dump the full JSON immediately.
Do not retry the call until you have read the actual response body.
Retrying blind on Shape C is how you burn rate-limit slots on the same
underlying failure.
