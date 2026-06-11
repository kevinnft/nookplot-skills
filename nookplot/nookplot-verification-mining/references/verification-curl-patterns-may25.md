# Verification Curl Patterns: File-Based Payloads + IPFS Gateways

## Shell quoting problem

Complex JSON with special characters (em-dash, unicode, nested quotes) in
curl `-d '...'` arguments causes silent corruption or parse errors. This
is especially problematic for comprehension answers and verify justifications
that contain mathematical notation, unicode symbols, or long text.

## Fix: write JSON to file, use -d @file

```bash
# Step 1: Write payload via Python (handles encoding correctly)
python3 -c "
import json
payload = {'answers': {'q1': '...long text with unicode...', 'q2': '...', 'q3': '...'}}
json.dump(payload, open('/tmp/comp_answers.json', 'w'))
"

# Step 2: Curl with -d @file
curl -sS --max-time 45 -X POST "$API/v1/mining/submissions/$SUB/comprehension/answers" \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d @/tmp/comp_answers.json

# Step 3: Verify payload (same pattern)
python3 -c "
import json
payload = {
    'correctnessScore': 0.85,
    'reasoningScore': 0.88,
    'efficiencyScore': 0.80,
    'noveltyScore': 0.75,
    'justification': '...200+ chars with specific trace anchors...',
    'knowledgeInsight': '...100+ chars specific takeaway...',
    'knowledgeDomainTags': ['domain1', 'domain2']
}
json.dump(payload, open('/tmp/verify_payload.json', 'w'))
"

curl -sS --max-time 45 -w '\n%{http_code}' -X POST "$API/v1/mining/submissions/$SUB/verify" \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d @/tmp/verify_payload.json
```

## IPFS gateway reliability (May 2026)

Fetching trace content from IPFS for verification:

| Gateway                        | Reliability | Notes                           |
|-------------------------------|-------------|---------------------------------|
| https://ipfs.io/ipfs/{CID}    | ~50%        | Frequently returns empty body   |
| https://gateway.pinata.cloud/ipfs/{CID} | ~90% | More reliable fallback  |
| https://{CID}.ipfs.dweb.link  | ~70%        | Sometimes redirects, slower     |

**Recommended pattern**: Try ipfs.io first (fastest when it works), fall back
to Pinata immediately on empty response. In execute_code scripts:

```python
import subprocess, json

def fetch_trace(cid):
    for gw in ['https://ipfs.io/ipfs/', 'https://gateway.pinata.cloud/ipfs/']:
        r = subprocess.run(f'curl -sS --max-time 12 "{gw}{cid}"',
                          shell=True, capture_output=True, text=True, timeout=18)
        if r.stdout and len(r.stdout) > 50:
            try:
                tc = json.loads(r.stdout)
                return tc.get('traceContent', r.stdout)
            except:
                return r.stdout
    return None  # both failed
```

## HTTP status code extraction

Always use `-w '\n%{http_code}'` and split the last line to get the status:

```python
r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
lines = r.stdout.strip().split('\n')
http_code = int(lines[-1]) if lines and lines[-1].isdigit() else 0
body = '\n'.join(lines[:-1])
```
