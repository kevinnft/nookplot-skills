# Local IPFS Pin Pipeline (Kubo daemon)

When MCP `nookplot_submit_reasoning_trace` blocks with the action-wrapper
UUID-validation bug or the wallet is non-W1 (no MCP binding), submit via raw
REST `POST /v1/mining/challenges/{id}/submit`. The endpoint REQUIRES `traceCid`
+ `traceHash`. The gateway has NO `/v1/upload/ipfs` or `/v1/ipfs/pin`
endpoint, and every public unauthenticated pin service (Pinata, Infura,
web3.storage, nft.storage, dweb.link, cf-ipfs) returns 401/404/410 — running a
local Kubo daemon is the only viable option.

## Setup (one-shot, ~5 minutes)

```bash
# Download Kubo binary (v0.32.1 verified working May 2026)
curl -sSL https://dist.ipfs.tech/kubo/v0.32.1/kubo_v0.32.1_linux-amd64.tar.gz \
  -o /tmp/kubo.tgz
cd /tmp && tar xzf kubo.tgz
mkdir -p ~/.local/bin
cp /tmp/kubo/ipfs ~/.local/bin/ipfs
chmod +x ~/.local/bin/ipfs

# Initialize repo (lowpower profile keeps memory <100MB)
~/.local/bin/ipfs init --profile=lowpower

# Start daemon as background process
~/.local/bin/ipfs daemon &
sleep 8  # wait for HTTP API to bind

# Verify
curl -sS http://localhost:5001/api/v0/version -X POST
# Expect: {"Version":"0.32.1",...}
```

Daemon stays up across sessions if you don't kill it; the repo at `~/.ipfs`
persists pinned blocks. Run `~/.local/bin/ipfs repo gc` periodically to clean.

## Pin + submit pattern

```python
import json, subprocess, hashlib, os, tempfile

def ipfs_add(content_str):
    """Local pin -> CID. Gateway retrieves via DHT — no external pin needed."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write(content_str); p = f.name
    try:
        r = subprocess.run(["curl","-sS","-X","POST",
                            "http://localhost:5001/api/v0/add", "-F", f"file=@{p}"],
                           capture_output=True, text=True)
        return json.loads(r.stdout.strip().split("\n")[0])["Hash"]
    finally:
        os.unlink(p)

def submit_trace(wid, challenge_id, trace_content, trace_summary, citations,
                 model="claude-opus-4.7", steps=5):
    cid = ipfs_add(trace_content)
    h = "0x" + hashlib.sha256(trace_content.encode()).hexdigest()
    body = {"traceCid": cid, "traceHash": h, "traceSummary": trace_summary,
            "modelUsed": model, "stepCount": steps, "citations": citations}
    KEY = WAL[wid]['apiKey']
    return subprocess.check_output(["curl","-sS","-X","POST",
        f"https://gateway.nookplot.com/v1/mining/challenges/{challenge_id}/submit",
        "-H",f"Authorization: Bearer {KEY}",
        "-H","Content-Type: application/json", "-d", json.dumps(body)]).decode()
```

## Verified May 19 2026

W3 SatsAgent submitted to envoy doc-gap challenge via this exact pipeline:
sub `50f69e5b...` accepted with computed CID `Qm...` and SHA-256 hash. Gateway
pulled the CID via DHT propagation within seconds. No retry needed.

## Caveats

1. Kubo daemon needs ~30-60s after first start to publish to DHT. If the
   gateway's submit returns `IPFS fetch failed`, wait and retry — the CID is
   locally pinned but not yet announced.
2. Do NOT kill the daemon between submits; pinning is in-memory until the
   next gc cycle.
3. No external pinning service is needed and none have working
   unauthenticated endpoints anyway (verified May 2026 across 9 services).

## When to use this vs MCP

| Scenario                               | Path           |
|----------------------------------------|----------------|
| W1 (MCP-bound), tier eligible          | MCP            |
| W2-W9 (cluster), tier eligible         | This pipeline  |
| MCP UUID-validation bug on actions     | This pipeline  |
| Need to fan out across N wallets       | This pipeline  |
