#!/usr/bin/env python3
"""
Submit a reasoning trace to a mining challenge at a target unlock time.

Pattern: upload to IPFS NOW (cheap, no rate limit), then block in a
sleep-loop until the wallet's GX 24h cap unlocks, then fire the submit.
This is the right shape when (a) a guild deep-dive challenge has slots open
but (b) the chosen wallet just submitted a different GX in the past 24h.

USAGE:
  python3 submit_at_unlock.py <walletKey> <tracePath> <targetIso> <summaryPath> <citationsCsv>

ARGS:
  walletKey      W2|W3|...|W9
  tracePath      /tmp/panda_trace1.md
  targetIso      2026-05-19T23:42:30+00:00 (the rolling 24h unlock from oldest
                 GX submission timestamp + 24h, plus ~30s safety margin)
  summaryPath    /tmp/summary.txt — 50-1000 chars, must pass anti-slop gate
                 (numbers/methods, no filler)
  citationsCsv   "arxiv:2505.13755,arxiv:2403.07815"

OUTPUTS:
  /tmp/panda_state/<wallet>_subid.txt — submission UUID on success.
  Logs to stdout.

PRE-FLIGHT (run once before scheduling):
  Probe oldest GX in 24h window per wallet:
    1. POST /v1/actions/execute with {"toolName":"my_mining_submissions",
       "args":{"address":<addr>,"limit":15}} to list recent sub IDs.
    2. For each, GET /v1/mining/submissions/{sid} → submittedAt + challengeId.
    3. For each unique challengeId, GET /v1/mining/challenges/{cid} →
       minGuildTier. If minGuildTier != "none", it counts as GX.
    4. unlock_time = oldest_gx_in_window.submittedAt + 24h + 30s margin.

PITFALLS:
  - Use Authorization: Bearer <key>, NOT X-API-Key.
  - The submit endpoint is /v1/mining/challenges/{id}/submit (direct REST).
    /v1/actions/execute with toolName:submit_reasoning_trace returns
    CHALLENGE_FETCH_FAILED — that path is broken for cross-wallet submits.
  - guildId in the body must match the wallet's current guild (call
    my_guild_status first); a stale ID silently drops the guild boost.
  - Tier0 Doc-gaps and tier1+ Guild deep-dives share the SAME GX counter.
"""
import sys, time, subprocess, json, hashlib
from datetime import datetime, timezone
from pathlib import Path

GW = "https://gateway.nookplot.com"

def submit(wallet_key, trace_path, summary, target_iso, citations,
           challenge_id, model_used="claude-opus-4.7-thinking", step_count=8):
    wallets = json.load(open('/home/asus/.hermes/nookplot_wallets.json'))
    w = wallets[wallet_key]
    api = w['apiKey']

    trace = Path(trace_path).read_text()
    th = hashlib.sha256(trace.encode()).hexdigest()

    # Resolve guildId live (don't rely on stale state file)
    g = subprocess.run(
        ['curl','-s','-X','POST',f"{GW}/v1/actions/execute",
         '-H',f"Authorization: Bearer {api}",
         '-H','Content-Type: application/json',
         '-d', json.dumps({"toolName":"my_guild_status","args":{}})],
        capture_output=True, text=True, timeout=20)
    gd = json.loads(g.stdout)
    res = gd.get('result', gd)
    if isinstance(res, str):
        try: res = json.loads(res)
        except Exception: pass
    gid = res.get('guildId') if isinstance(res, dict) else None
    print(f"[{wallet_key}] resolved guildId={gid}", flush=True)

    # IPFS upload BEFORE the wait — fail fast on auth/network problems
    ub = {"data": {"content": trace, "format": "markdown",
                   "uploadedAt": datetime.now(timezone.utc).isoformat()[:19]+"Z"},
          "name": f"trace-{challenge_id[:8]}-{wallet_key.lower()}"}
    r = subprocess.run(
        ['curl','-s','-X','POST',f"{GW}/v1/ipfs/upload",
         '-H',f"Authorization: Bearer {api}",
         '-H','Content-Type: application/json',
         '--data-binary', json.dumps(ub)],
        capture_output=True, text=True, timeout=60)
    upl = json.loads(r.stdout)
    cid = upl.get('cid')
    if not cid:
        print(f"[{wallet_key}] IPFS upload FAILED: {r.stdout[:500]}", flush=True)
        return None
    print(f"[{wallet_key}] IPFS pinned cid={cid} size={upl.get('size')}", flush=True)

    # Block until target time
    target = datetime.fromisoformat(target_iso)
    while True:
        now = datetime.now(timezone.utc)
        rem = (target - now).total_seconds()
        if rem <= 0: break
        print(f"[{wallet_key}] {now.strftime('%H:%M:%S UTC')} wait {rem:.0f}s", flush=True)
        time.sleep(min(60, max(5, rem)))

    # Submit
    sb = {"traceCid": cid, "traceHash": th, "traceSummary": summary,
          "modelUsed": model_used, "stepCount": step_count,
          "citations": citations, "guildId": gid}
    r = subprocess.run(
        ['curl','-s','-X','POST',
         f"{GW}/v1/mining/challenges/{challenge_id}/submit",
         '-H',f"Authorization: Bearer {api}",
         '-H','Content-Type: application/json',
         '--data-binary', json.dumps(sb)],
        capture_output=True, text=True, timeout=120)
    print(f"[{wallet_key}] SUBMIT response:\n{r.stdout[:2500]}", flush=True)

    try:
        d = json.loads(r.stdout)
        if 'id' in d:
            state_dir = Path('/tmp/panda_state')
            state_dir.mkdir(exist_ok=True)
            (state_dir / f'{wallet_key}_subid.txt').write_text(d['id'])
            return d['id']
    except Exception:
        pass
    return None

if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("usage: submit_at_unlock.py <wallet> <tracePath> <targetIso> "
              "<summaryPath> <citationsCsv> <challengeId>")
        sys.exit(2)
    wallet = sys.argv[1]
    trace_path = sys.argv[2]
    target_iso = sys.argv[3]
    summary_path = sys.argv[4]
    cites = sys.argv[5].split(',') if sys.argv[5] else []
    challenge_id = sys.argv[6]
    summary = Path(summary_path).read_text().strip()
    submit(wallet, trace_path, summary, target_iso, cites, challenge_id)
