# 24h Cap Audit — Per-Wallet Submission Window

**Use case:** answering "sudah maksimal?" / "kapan bisa lanjut?" with real timestamps for each cluster wallet.

## The cap rule (verified May 18 2026)

- Per-wallet daily mining cap = 12 submissions in a **rolling 24h window** (not UTC midnight reset).
- Window unlock = `oldest_submission_timestamp_in_window + 24h`. Earliest sub falls out, slot opens.
- Cluster aggregate cap = 9 × 12 = 108/day, but per-wallet enforcement is independent.

## REST endpoint that actually works

```
GET https://gateway.nookplot.com/v1/mining/submissions/{uuid}
Auth: Bearer nk_<wallet_apiKey>
```
Returns the submission as a native JSON object with `createdAt`, `solverGuildId`, `traceCid`, `traceSummary`, `modelUsed`, etc. This is the path that gives reliable per-submission timestamps.

## Pitfall: MCP `nookplot_get_reasoning_submission` is broken for these UUIDs

Calling `nookplot_get_reasoning_submission({"submissionId":"89ff9735-2b67-492a-9ccb-5d56cd0483c6"})` returns:
```
{"status":"error","error":"Invalid submission ID format. Must be a UUID."}
```
The ID *is* a valid UUID. The MCP tool's pre-validator is mismatched against the gateway's id format. Workaround: hit the REST endpoint directly. Same auth, same wallet apiKey, returns the full object.

`nookplot_access_mining_trace` MCP tool fails the same way — same workaround.

## Listing endpoint pitfalls

- `GET /v1/mining/submissions` (without an ID) returns 404 — this listing endpoint does not exist.
- `GET /v1/mining/submissions?address=0x...&limit=N` returns 404 too.
- The only listing path is the MCP tool `nookplot_my_mining_submissions({"limit":50})`. It returns a markdown-formatted string, not a JSON array. Parse the table to extract the 36-char UUIDs at the bottom of the markdown:
  ```python
  import re
  ids = re.findall(r'`([0-9a-f-]{36})`', md_string)
  ```
- The markdown rows show `Date` as `May 18` only (no time). For exact UTC timestamps you MUST resolve each ID via REST `/v1/mining/submissions/{uuid}`.

## Drop-in script (parallel-safe, ~30 sec for 9 wallets × 25 ids)

```python
import subprocess, json, re, concurrent.futures
from datetime import datetime, timezone, timedelta
W = json.load(open('/home/asus/.hermes/nookplot_wallets.json'))

def call_mcp(api, tool, inp=None):
    p = json.dumps({"toolName": tool, "input": inp or {}})
    r = subprocess.run(['curl','-sk','--max-time','15','-H',f'Authorization: Bearer {api}',
        '-H','Content-Type: application/json','-X','POST','-d',p,
        'https://gateway.nookplot.com/v1/actions/execute'], capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        if d.get('status')=='completed': return d.get('result')
    except: pass
    return None

def get_sub_detail(api, sid):
    r = subprocess.run(['curl','-sk','--max-time','8','-H',f'Authorization: Bearer {api}',
        f'https://gateway.nookplot.com/v1/mining/submissions/{sid}'], capture_output=True, text=True)
    try: return json.loads(r.stdout)
    except: return None

# 1) collect IDs (parallel across 9 wallets)
def fetch_ids(k):
    md = call_mcp(W[k]['apiKey'], 'nookplot_my_mining_submissions', {'limit':50}) or ''
    return k, re.findall(r'`([0-9a-f-]{36})`', md)[:25]

ids_per_w = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=9) as ex:
    for k, ids in ex.map(fetch_ids, list(W.keys())):
        ids_per_w[k] = ids

# 2) resolve timestamps (parallel)
def resolve(args):
    k, sid = args
    d = get_sub_detail(W[k]['apiKey'], sid)
    if not isinstance(d, dict): return k, None
    ts = d.get('createdAt') or d.get('submittedAt') or d.get('timestamp')
    if not ts: return k, None
    if isinstance(ts, str):
        try: t = datetime.fromisoformat(ts.replace('Z','+00:00'))
        except: return k, None
    else:
        t = datetime.fromtimestamp(ts/1000 if ts > 1e12 else ts, timezone.utc)
    return k, t

tasks = [(k, sid) for k, ids in ids_per_w.items() for sid in ids]
results = {k: [] for k in W}
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    for k, t in ex.map(resolve, tasks):
        if t: results[k].append(t)

# 3) compute unlock window per wallet
now = datetime.now(timezone.utc)
CAP = 12
for k in sorted(W):
    times = sorted(results[k])
    in24 = [x for x in times if (now - x).total_seconds() < 86400]
    if in24:
        oldest = min(in24)
        unlock = oldest + timedelta(hours=24)
        delta_s = (unlock - now).total_seconds()
        if delta_s > 0:
            unlock_str = f"{int(delta_s//3600)}h{int((delta_s%3600)//60)}m"
        else:
            unlock_str = "OPEN"
    else:
        unlock_str = "OPEN"
    open_slots = max(0, CAP - len(in24))
    print(f"{k}  in24={len(in24):2d}/12  unlock={unlock_str:8s}  slots_open={open_slots}")
```

## Reporting shape (matches user's "cek ulang" expectation)

For each wallet show: guild, boost, 24h count vs cap, oldest_24h_UTC, newest_UTC, unlock UTC + WIB + relative `Xh Ym`. Then a sorted ETA list of unlocks (earliest first) so user can plan polling.

## Wallets to prioritize when slots are open

Higher boost first, then higher historical totalEarned (proxy for verifier consensus quality):
1. W2 SocialContract tier2 1.6x (top earner ~1.4M lifetime)
2. W6/W7/W8/W9 Jetpack tier2 1.6x (newer, fresh slots often available)
3. W3 SatsAgent tier1 1.35x
4. W1/W4 Lyceum 1.0x
5. W5 QuillEdge 1.0x
