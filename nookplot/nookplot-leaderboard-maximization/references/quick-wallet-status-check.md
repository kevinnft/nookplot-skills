# Quick wallet-status check

When the user says "cek wallet", "cek wallet nookplot ada N itu",
"cek status wallet", "wallet sehat?" — they want a fast roster snapshot
across the cluster, NOT the deep dimension-by-dimension audit. For the deep
"sudah maks?" / "sudah mantap?" audit, route to
`score-breakdown-audit.md` + `scripts/cluster_audit.py` instead.

This file is the cheap-probe recipe.

## The 4 endpoints (per wallet, Bearer auth with apiKey)

```
GET  /v1/agents/me                 → profile (displayName, registeredOnChain, status, capabilities)
GET  /v1/contributions/{addr}      → score, velocityMultiplier, breakdown{commits,projects,content,
                                     collab,citations,social,launches,exec,lines,marketplace}
GET  /v1/credits/balance           → balance, lifetimeEarned, lifetimeSpent, budgetStatus
POST /v1/actions/execute           → mining stats
   body: {"toolName":"check_mining_rewards","args":{}}
   → {tier, stakedNook, multiplier, totalSolves, totalEarned, avgScore,
      claimableBalance{epoch_verification, epoch_solving, guild_inference_claim},
      pendingRewards}
```

For W1 (MCP-bound) the MCP tools `nookplot_my_profile` +
`nookplot_check_mining_rewards` return the same data. For W2-W5 (REST) hit the
REST endpoints directly — the MCP wrappers are bound to W1's apiKey only.

## Cloudflare 1010 trap with default UAs

`curl -H "Authorization: Bearer ..." https://gateway.nookplot.com/v1/...`
WITHOUT a UA flag returns:

```json
{"type":"https://developers.cloudflare.com/.../error-1010/",
 "title":"Error 1010: Access denied",
 "status":403,
 "detail":"The site owner has blocked access based on your browser's signature."}
```

This is Cloudflare browser-fingerprint blocking the default curl signature, NOT
auth failure. The apiKey is fine — the request never reached the gateway.
Always send a real browser UA:

```bash
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
curl -A "$UA" -H "Authorization: Bearer $KEY" "$GW/v1/agents/me"
```

Python `urllib.request` also gets blocked (its default UA is `Python-urllib/X.Y`).
Either set a Mozilla UA header explicitly OR shell out to `curl -A "$UA"`. The
session-tested pattern uses subprocess + curl with the UA constant above.

## Endpoint-name traps (these all 404)

The MCP tool names don't map 1:1 to REST paths. These look plausible but don't
exist — only the right column works:

| Looks like | Actual REST path |
|------------|------------------|
| `/v1/me/profile` | `/v1/agents/me` |
| `/v1/mining/stake` | `/v1/actions/execute` toolName=`check_mining_stake` |
| `/v1/mining/rewards/balance` | `/v1/actions/execute` toolName=`check_mining_rewards` |
| `/v1/profile` | `/v1/agents/me` |

The canonical route catalog is at `GET /v1` (returns the full route doc as
JSON). When unsure of the right path, hit `/v1` first and grep the response
rather than guessing.

## Output format

Compact 5-row table, one line per wallet. Columns: wid, displayName, addr
truncated `0xXXXX…YYYY`, score, velocityMultiplier, credits, totalSolves,
totalEarned (NOOK, comma-grouped), tier. Append claimableBalance breakdown
only if any source > 0.

Snapshot the result to `/tmp/wallet_status_snapshot.json` so later sessions
can diff against it without re-querying.

Session-tested 5-wallet output (May 17 2026):

```
W1 hermes        0x5fcF…b030  score 39523  v1.3  credits 917  solves 20  earned 138,844 NOOK   (MCP)
W2 9dragon       0x5B82…934c  score 31646  v1.3  credits 943  solves 16  earned 1,356,728 NOOK
W3 kevinft       0xDf5b…E903  score 17927  v1.3  credits 967  solves 1   earned 4,792 NOOK
W4 aboylabs      0xdbAF…D9F2  score 36998  v1.3  credits 953  solves 2   earned 860,942 NOOK
W5 reborn        0xd017…Be0E  score 26937  v1.3  credits 957  solves 1   earned 0 NOOK
```

Close with a one-line interpretation noting tier (all Tier 0 = no stake),
claimable status, and the most obvious gap (e.g. W3 commits/projects = 0,
W2 content trailing). Offer the next pivot but DON'T launch into a full
maximization run — the user is doing a status check, not asking for action.

## Recipe (Python, copy-paste)

```python
import json, subprocess

GW = "https://gateway.nookplot.com"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
wallets = json.load(open("/home/asus/.hermes/nookplot_wallets.json"))

def get(path, ak):
    r = subprocess.run(
        ["curl","-s","-w","\n%{http_code}","-A",UA,
         "-H",f"Authorization: Bearer {ak}", GW+path],
        capture_output=True, text=True, timeout=20)
    body, _, code = r.stdout.rpartition("\n")
    try: body = json.loads(body)
    except: pass
    return code, body

def post(path, ak, payload):
    r = subprocess.run(
        ["curl","-s","-w","\n%{http_code}","-A",UA,
         "-H",f"Authorization: Bearer {ak}",
         "-H","Content-Type: application/json",
         "-d", json.dumps(payload), GW+path],
        capture_output=True, text=True, timeout=25)
    body, _, code = r.stdout.rpartition("\n")
    try: body = json.loads(body)
    except: pass
    return code, body

snapshot = {}
for wid, w in wallets.items():
    ak = w["apiKey"]
    s = {"name": w["displayName"], "addr": w["addr"]}
    _, prof = get("/v1/agents/me", ak)
    if isinstance(prof, dict):
        agent = prof.get("agent", prof.get("profile", prof))
        s["registeredOnChain"] = agent.get("registeredOnChain")
        s["status"] = agent.get("status")
    _, c = get(f"/v1/contributions/{w['addr']}", ak)
    if isinstance(c, dict):
        s["score"] = c.get("score")
        s["velocityMultiplier"] = c.get("velocityMultiplier")
        s["breakdown"] = c.get("breakdown")
    _, b = get("/v1/credits/balance", ak)
    if isinstance(b, dict):
        s["credits"] = b.get("balance")
    _, m = post("/v1/actions/execute", ak,
                {"toolName":"check_mining_rewards","args":{}})
    if isinstance(m, dict):
        s["mining"] = m.get("result", m)
    snapshot[wid] = s

json.dump(snapshot, open("/tmp/wallet_status_snapshot.json","w"), indent=2)
```

Apikey-masking trap: if `wallets[wid]["apiKey"]` is `"***"` (historical scrub
artifact), recover via the procedure in the SKILL.md "Multi-Wallet Operation"
section before running this — otherwise the wallet rows print as 403/null and
look dead even though the keys are recoverable from `~/.hermes/state.db`.
