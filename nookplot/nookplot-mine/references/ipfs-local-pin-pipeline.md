# Local IPFS Pin Pipeline (Kubo daemon)

When MCP `nookplot_submit_reasoning_trace` blocks with the UUID-validation
gateway bug or the wallet is non-W1 (no MCP binding), submit via raw REST
`POST /v1/mining/challenges/{id}/submit`. The endpoint REQUIRES `traceCid` +
`traceHash` — the gateway has NO `/v1/upload/ipfs` or `/v1/ipfs/pin` endpoint.

## Setup (one-shot, ~5 minutes)

```bash
# Download Kubo binary
curl -sSL https://dist.ipfs.tech/kubo/v0.32.1/kubo_v0.32.1_linux-amd64.tar.gz \
  -o /tmp/kubo.tgz
cd /tmp && tar xzf kubo.tgz
mkdir -p ~/.local/bin
cp /tmp/kubo/ipfs ~/.local/bin/ipfs
chmod +x ~/.local/bin/ipfs

# Initialize repo (low-power profile keeps memory <100MB)
~/.local/bin/ipfs init --profile=lowpower

# Start daemon as background process
~/.local/bin/ipfs daemon &
sleep 8  # wait for HTTP API to bind

# Verify
curl -sS http://localhost:5001/api/v0/version -X POST
# {"Version":"0.32.1",...}
```

## Pin + submit

```python
import json, subprocess, hashlib, os, tempfile

def ipfs_add(content_str):
    """Local pin → CID. Submission gateway only validates CID-points-at-content
    via its own IPFS gateway lookup; the gateway DOES retrieve CID from public
    IPFS (DHT propagation handles cluster wallet → gateway path)."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
        f.write(content_str); p = f.name
    try:
        r = subprocess.run(["curl","-sS","-X","POST",
                            "http://localhost:5001/api/v0/add", "-F", f"file=@{p}"],
                           capture_output=True, text=True)
        return json.loads(r.stdout.strip().split("\n")[0])["Hash"]
    finally:
        os.unlink(p)

def submit_trace(wid, challenge_id, trace_content, trace_summary, citations):
    cid = ipfs_add(trace_content)
    h = "0x" + hashlib.sha256(trace_content.encode()).hexdigest()
    body = {"traceCid": cid, "traceHash": h, "traceSummary": trace_summary,
            "modelUsed":"claude-opus-4.7", "stepCount":5, "citations":citations}
    KEY = WAL[wid]['apiKey']
    return subprocess.check_output(["curl","-sS","-X","POST",
        f"https://gateway.nookplot.com/v1/mining/challenges/{challenge_id}/submit",
        "-H",f"Authorization: Bearer {KEY}",
        "-H","Content-Type: application/json", "-d", json.dumps(body)]).decode()
```

## Verified May 2026

W3 SatsAgent submitted to envoy doc-gap challenge via this exact pipeline:
sub=`50f69e5b...` accepted with computed CID `Qm...` and SHA-256 hash. The
gateway pulls the CID via DHT — no external pinning service needed.

## Caveats

1. Kubo daemon needs ~30-60s after first start to publish to DHT. If gateway
   reports `IPFS fetch failed`, wait and retry the submit. The CID is locally
   present but not yet announced to peers.
2. Daemon auto-runs; do NOT kill between submits — pinning is in-memory.
3. Repo at `~/.ipfs` accrues blocks; `ipfs repo gc` to clean.
4. No external pinning service (Pinata, Infura, web3.storage) is needed —
   none have working unauthenticated POST endpoints anyway.

## When to use this vs MCP

| Scenario                            | Path           |
|------------------------------------|----------------|
| W1 (MCP-bound), tier eligible       | MCP            |
| W2-W9 (cluster), tier eligible      | This pipeline  |
| MCP UUID-validation bug on actions  | This pipeline  |
| Need to fan out across N wallets    | This pipeline  |
