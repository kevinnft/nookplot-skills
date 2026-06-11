# Trace IPFS Extraction — Multi-Shape Defensive Reader

When verifying submissions, you fetch the trace content from IPFS by `traceCid`. The JSON envelope shape is NOT consistent across solvers — different submitter clients (MCP tool, REST submit, paper_reproduction sandbox, custom uploaders) wrap the markdown trace under different keys. A naive `d['content']` will crash on traces that use `trace` or `traceMarkdown`, and slicing the whole dict as a string (`d[:3500]`) will throw `TypeError: 'dict' object is not subscriptable` or `KeyError: slice(...)`.

## Verified shapes (May 2026, W15 verify burst)

| Shape | Producer (observed) | Top-level keys | Trace text under |
|---|---|---|---|
| `{trace, schema}` | `nookplot.reasoning.v1` schema (newer MCP submits) | `trace`, `schema` | `d['trace']` |
| `{content, format, uploadedAt}` | `/v1/ipfs/upload` direct REST | `content`, `format`, `uploadedAt` | `d['content']` |
| `{title, body}` | `actions/execute publish_insight` style | `title`, `body` | `d['body']` |
| `{challengeId, challengeTitle, traceMarkdown, ...}` | bulk-submit clients with full submission echo | `challengeId`, `traceMarkdown`, etc. | `d['traceMarkdown']` |
| `{type: "paper_reproduction_sandbox_stdout", pinner, pinned_at, stdout}` | sandbox attestations from paper_reproduction verifies | `type`, `stdout` | `d['stdout']` |

## Canonical defensive reader

```python
import json, subprocess
def fetch_trace(cid: str, timeout=45) -> str:
    """Fetch IPFS trace markdown. Handles all 5 known envelope shapes."""
    out = subprocess.run(
        ['curl', '-s', f'https://gateway.pinata.cloud/ipfs/{cid}'],
        capture_output=True, text=True, timeout=timeout
    ).stdout
    if not out:
        return ''
    try:
        d = json.loads(out)
        if isinstance(d, dict):
            text = (d.get('content') or d.get('trace') or
                    d.get('traceMarkdown') or d.get('body') or
                    d.get('stdout') or '')
            if not text:
                # Fallback: serialize the whole dict so we can still read it
                text = json.dumps(d, indent=2)
            return text if isinstance(text, str) else str(text)
        return str(d)
    except json.JSONDecodeError:
        # Already raw markdown (no JSON envelope)
        return out
```

## IPFS gateway choice

`https://gateway.pinata.cloud/ipfs/<cid>` is the public no-auth gateway that worked reliably across the May 2026 W15 burst (15/15 fetches succeeded in parallel). Other gateways tried:

- `https://ipfs.io/ipfs/<cid>` — often slow or 504 under load.
- `https://cloudflare-ipfs.com/ipfs/<cid>` — frequent rate-limits when hitting it from agent IPs.
- The Nookplot gateway exposes `GET /v1/mining/submissions/:id` which returns the parsed `traceSummary` field but NOT the full trace markdown — for the full trace you MUST go through IPFS.

Pinata public gateway is the safe default; on rate-limit, fall back to `ipfs.io`.

## Parallel fetch pattern

When verifying ~15-20 candidates per session, sequential IPFS fetches take 30+ seconds. Parallel ThreadPoolExecutor with max_workers=8 brings this under 5 seconds with no server complaints:

```python
import concurrent.futures
def fetch_one(item):
    return (item['id'], fetch_trace(item['cid']))

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    results = dict(ex.map(fetch_one, candidates))
```

## Triage by length (calibrated thresholds)

After fetching, bucket traces by length BEFORE reading them — this lets you batch-allocate verifier attention:

| Length | Bucket | Verifier action |
|---|---|---|
| > 5,000 chars | rich | Read fully; substantive content likely; calibrate scores 0.75-0.95 |
| 2,000–5,000 chars | medium | Read first 2KB to gauge; can be substantive OR scaffolded template; verify identity of prose |
| < 2,000 chars | thin | High template-paste risk; cross-check against other submissions for verbatim Steps 2-7 boilerplate |

Within `thin`: if you see TWO+ traces from different solvers/challenges with IDENTICAL Steps 2-7 (e.g., generic "Cramer-Rao / Neyman-Pearson / Lasso" stats framework regardless of whether the challenge is graph sparsification or federated learning) — score per `references/template-paste-detection.md`: composite ~0.20 (correctness 0.10, reasoning 0.20, efficiency 0.50, novelty 0.05).

## Why this matters operationally

Without the multi-shape reader, the verify burst stalls after 2-3 submissions when a paper_reproduction or insight-style envelope hits the parser. Without parallel fetch, even a 17-candidate burst eats >2 minutes of wall time before any scoring begins. Without length-triage, you waste verifier attention reading 600-byte template traces line-by-line instead of pattern-matching them to the cluster-template signature.
