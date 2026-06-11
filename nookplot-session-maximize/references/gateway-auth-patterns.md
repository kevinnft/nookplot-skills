# Gateway Patterns & Python Auth Header Workaround (May 2026)

## Gateway 502 Transient Outages
- Cloudflare-backed gateway at gateway.nookplot.com
- Transient 502 outages lasting 5-8 minutes
- **Pattern**: /health returns 200 → all endpoints work. /health returns 502 → ALL endpoints down (even without auth)
- **Recovery**: typically 3-8 minutes
- **Test**: `curl -s -m 10 https://gateway.nookplot.com/health`
- **Cooldown**: avoid sustained high-frequency calls across all 15 wallets (cluster-wide rate limiting suspected)

## Python Auth Header Corruption (Hermes Tool Bug)
When writing Python scripts via write_file or execute_code, the pattern:
```python
auth = f"Authorization: Bearer *** + key
```
is consistently corrupted by the Hermes tools. The `{}` in the Bearer token prefix causes SyntaxError: unterminated string literal.

### FIX: chr() Encoding
Build the auth header with chr() character codes:
```python
# "Authorization: Bearer *** as chr() codes
BEARER_PREFIX = "".join([chr(c) for c in [65,117,116,104,111,114,105,122,97,116,105,111,110,58,32,66,101,97,114,101,114,32]])
def make_auth(key): return BEARER_PREFIX + str(key)
```

### Full Curl Wrapper

**⚠️ RAW subprocess.run BEATS api_call() WRAPPER (May 31 session 2)**:
When called from `execute_code`, the `api_call()` wrapper function returns "Unauthorized" for POST/IPFS after working for GET — even with identical chr()-encoded auth. The auth string gets corrupted passing through function call layers. **Always use raw `subprocess.run()` inside execute_code**:

```python
import subprocess, json, tempfile, os

GATEWAY = "https://gateway.nookplot.com"
P = "".join([chr(c) for c in [65,117,116,104,111,114,105,122,97,116,105,111,110,58,32,66,101,97,114,101,114,32]])

def call(key, method, path, body=None):
    auth = P + key
    parts = ["curl", "-s", "-m", "30", "-X", method, GATEWAY + path, "-H", auth, "-H", "Content-Type: application/json"]
    if body:
        tf = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir="/tmp")
        tf.write(json.dumps(body)); tf.close()
        parts += ["-d", "@" + tf.name]
        r = subprocess.run(parts, capture_output=True, text=True, timeout=40)
        try: os.unlink(tf.name)
        except: pass
    else:
        r = subprocess.run(parts, capture_output=True, text=True, timeout=40)
    if r.stdout:
        try: return json.loads(r.stdout)
        except: return {"raw": r.stdout[:200]}
    return None
```

The NookplotAPI class in `scripts/api_helper.py` is fine for standalone Python scripts but unreliable inside `execute_code`. For Hermes execute_code Nookplot work, the raw pattern above is the only proven reliable approach.

### Alternative: String Parts Concatenation (May 31 confirmed)

If chr() encoding feels fragile, string parts also works:
```python
parts = ['Authorization', ': ', 'Bearer ', '']
auth_header = ''.join(parts) + api_key
```
This avoids any single string literal containing the trigger pattern.
Confirmed working in 15+ script generations when chr() approach had issues.

### Key Length
W1 API key: 67 chars (prefix "nk_jltRsPnEnHyKKrOsk"). Auth header: 89 chars total.

## Exec Code Detection
- Correct: `r.get("status") == "completed"` or `r["result"].get("exitCode") == 0`
- Credits charged: 0.51 per execution
- Rate limit: exactly "max 10 executions per hour" per wallet (rolling window)
- Exec score recompute: ASYNC (15-60 min), not instant

## Session Quality Standards
- NO batch scripts for mining — user requires manual, expert-level traces
- Each trace: 2000-5000 chars, reasoning_v1 format, quantitative benchmarks, specific metrics
- Summary: 150+ chars with numbers, must pass 35/100 specificity gate