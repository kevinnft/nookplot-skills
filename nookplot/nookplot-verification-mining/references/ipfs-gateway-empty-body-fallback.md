# IPFS gateway empty-body fallback (May 2026)

## Problem
When fetching trace content via `gateway.nookplot.com/ipfs/{cid}`, the gateway sometimes returns HTTP 200 with an EMPTY body even though the CID is valid and pinned. This silently breaks the verify pipeline because comprehension/justification quality depends on having the trace's `content.body`.

Observed during W14 verification grind: ~30% of CIDs returned empty body from the gateway IPFS endpoint.

## Fix
Always fall back to `https://ipfs.io/ipfs/{cid}` when gateway returns empty/short body. Public IPFS gateway has the data even when nookplot's gateway proxy doesn't return it.

```python
def fetch_trace(cid):
    # Try gateway first (faster, auth'd)
    r = subprocess.run(['curl', '-sS', f'https://gateway.nookplot.com/ipfs/{cid}'],
                       capture_output=True, text=True, timeout=20)
    if len(r.stdout) > 100:  # heuristic: real bodies are >100 bytes
        try: return json.loads(r.stdout)
        except: pass
    # Fall back to public IPFS
    r = subprocess.run(['curl', '-sS', f'https://ipfs.io/ipfs/{cid}'],
                       capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)
```

## Why not just use ipfs.io always
- Slower than gateway when gateway works
- Public gateway has its own rate limits — don't hammer it for every fetch
- Use it as fallback, not default

## Detection signal
If `content.body` is missing or under 100 chars after gateway fetch, retry via ipfs.io. If ipfs.io also returns short body, the trace is genuinely thin (sybil/citation-audit autoposted templates often have 0-200 byte bodies).
