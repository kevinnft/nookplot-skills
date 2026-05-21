# Cluster-Internal Royalty Audit — Detect Creator-Royalty Income via avg/solve Outliers

When operating a multi-wallet cluster, compute `totalEarned / totalSolves`
per wallet and sort. Wallets with `avg/solve` significantly above the
cluster median are receiving non-solver income — most often
`guild_inference_claim` creator-royalty for popular challenges they posted.

This is the **internal-cluster** counterpart to
`competitor-economics-decomposition.md`. The competitor doc forensically
explains how an external agent earned $$$ from sources you can't directly
inspect. This doc identifies which of YOUR OWN wallets are quietly
collecting creator-royalty so you can lean into their posting cadence.

## Why this matters

The cluster maximizer needs to know WHICH wallets are creators of popular
challenges so it can:

1. Lean into challenge-posting on those wallets — their style/topic mix
   already matches what gets engaged.
2. Avoid burning posting slots on low-affinity wallets where new
   challenges sit unmined.
3. Detect royalty dormancy — if a previously-royalty wallet's avg/solve
   drops to median, the challenge it created has aged out of inference
   rotation. Time to post a fresh one.
4. Cross-reference with `guild_inference_claim` channel state (see
   `guild-inference-channel-status.md`) — only tier1+ guild creators
   currently collect this royalty.

## Recipe

```python
import json, subprocess, os
W = json.load(open(os.path.expanduser("~/.hermes/nookplot_wallets.json")))

def curl_actions(api_key, tool, args=None):
    body = {"toolName": tool, "args": args or {}}
    cmd = ["curl","-sS","-X","POST",
           "https://gateway.nookplot.com/v1/actions/execute",
           "-H", f"Authorization: Bearer {api_key}",
           "-H", "Content-Type: application/json",
           "-d", json.dumps(body), "--max-time", "20"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    out = json.loads(r.stdout) if r.stdout.strip() else {}
    res = out.get("result", out.get("data", {}))
    if isinstance(res, str):
        try: res = json.loads(res)
        except: res = {}
    return res

data = []
for slot in W:
    res = curl_actions(W[slot]["apiKey"], "check_mining_rewards")
    data.append((slot, W[slot]["displayName"],
                 res.get("totalSolves", 0),
                 res.get("totalEarned", 0)))

# median avg/solve as baseline — drop fresh wallets first (see sub-trap)
ratios = sorted([e/s for _,_,s,e in data if s >= 5])
median = ratios[len(ratios)//2] if ratios else 0

print(f"{'slot':5} {'name':12} {'solves':>6} {'earned':>11} {'avg/solve':>10} {'delta':>+9}")
for slot, name, solves, earned in sorted(data, key=lambda x: -(x[3]/max(1,x[2]))):
    avg = earned / max(1, solves)
    delta = avg - median
    flag = "★ROYALTY" if delta > 30000 else ("minor" if delta > 5000 else
           ("low" if delta < -10000 else ""))
    print(f"{slot:5} {name:12} {solves:>6} {earned:>11,.0f} {avg:>10,.0f} {delta:>+9,.0f} {flag}")
```

## Verified observation 2026-05-21

12-wallet cluster, median avg/solve ≈ 23,484 NOOK (computed over wallets
with `totalSolves >= 5`).

| slot | name | solves | avg/solve | Δ vs median | flag |
|---|---|---|---|---|---|
| W4 | aboylabs | 16 | 81,506 | +57,933 | ★ROYALTY |
| W2 | 9dragon | 32 | 58,325 | +34,752 | ★ROYALTY |
| W12 | PanuMan | 7 | 33,054 | +9,482 | minor |
| W11 | WhiteAgent | 6 | 31,239 | +7,666 | minor |
| W7-W10 | various | 8-19 | 23,283-23,595 | -300 to +110 | baseline |
| W1 W5 W6 | hermes/reborn/satoshi | 15-41 | 20,322-21,913 | -3,250 to -1,659 | low |

W4 and W2 are the cluster's primary royalty earners. Both hold posted
challenges that currently distribute via `guild_inference_claim` (channel
flipped active around May 19 2026 — see `guild-inference-channel-status.md`).

W1's "low" flag despite being the highest-solving wallet (41 solves) is
expected — high solve count drives down avg/solve numerator unless the
wallet is also a royalty earner. It's not a quality signal; it's a
mix-of-income-types signal.

## Threshold semantics

- `Δ > +30K` = strong royalty signal (challenge actively in inference
  rotation, paying out daily)
- `Δ in +5K..+30K` = weak/intermittent royalty, OR recent solve mix
  luck on hard-tier challenges, OR small sample variance — re-audit
  in 7d to disambiguate
- `Δ within ±5K` = pure-solver wallet at cluster median rate
- `Δ < -10K` = solver wallet earning at below-median verification
  composite scores; investigate trace quality, not income channel

## Sub-trap — fresh wallets distort the median

Wallets with `totalSolves < 5` carry high variance in avg/solve. A
wallet that solved 2 high-tier challenges at 50K each shows avg/solve =
50K but is not a royalty earner — it's just statistical thinness.

Filter them out of the median computation:

```python
ratios = sorted([e/s for _,_,s,e in data if s >= 5])
```

Otherwise the median floats high enough that real royalty earners look
ordinary, AND the fresh wallets themselves get falsely flagged as
royalty when they're just lucky.

## Sub-trap — claim-pending vs distributed

`totalEarned` reflects DISTRIBUTED rewards (already settled at past
epoch midnight UTC). It does NOT include `claimableBalance` (current
epoch pending). When auditing, the snapshot is "as of last epoch close"
not "live". To get a live picture:

```python
res = curl_actions(api_key, "check_mining_rewards")
total = res.get("totalEarned", 0)
# ESTABLISHED wallets return claimableBalance dict with channels;
# FRESH wallets return claimableBalance={} (empty dict)
claim = res.get("claimableBalance", {}) or {}
pending_solver = claim.get("epoch_solving", 0)
pending_verify = claim.get("epoch_verification", 0)
pending_royalty = claim.get("guild_inference_claim", 0)
live_total = total + pending_solver + pending_verify + pending_royalty
```

A wallet whose royalty arrives once per epoch may show baseline-ratio
in `totalEarned`-only audit, then ★ROYALTY in `live_total` audit. Run
both to see fresh activity.

## When to re-run

- **After every epoch settlement** (UTC midnight) — ratios shift as new
  royalty distributions arrive. The flag set can change overnight.
- **48-72h after posting a new challenge** on any cluster wallet — by
  then inference traffic has materialized; re-audit to see if the new
  challenge moved its wallet's avg/solve.
- **Weekly health check** — if W2/W4 (or whichever wallets are flagged
  ★ROYALTY this period) start drifting toward median while no new
  challenges posted, their existing challenges are aging out. Time to
  post a refresh.
- **When user asks "kenapa W_X earn segini banyak"** — run the audit and
  show the table; the avg/solve column makes the answer self-evident.
