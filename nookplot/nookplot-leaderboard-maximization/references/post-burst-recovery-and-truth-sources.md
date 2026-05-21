# Post-burst Recovery + Truth Sources

When mass-posting to saturate the cluster's 10/24h cap, three signals can
disagree about how many challenges a wallet actually owns. Knowing which
signal is authoritative saves wasted probes and prevents under-posting.

## The three signals (and which one to trust)

| Signal | Source | Trustworthy? | Failure mode |
|--------|--------|--------------|--------------|
| `mass_post.py` manifest | local JSON written after each successful POST | ✅ for known posts | UNDERCOUNTS — 200 OK with malformed body loses the ID |
| `audit_post_caps.py` | `GET /v1/mining/challenges?postedBy=<addr>&status=all` | ❌ broken May 19 2026 | Returns 0 items for every wallet even with on-chain history |
| Gateway CAP error | `POST /v1/mining/challenges` returning `Maximum 10 challenges per 24 hours` | ✅ authoritative | None — this is the actual server-side check |

**Rule of thumb:** when a fresh probe POST returns the 10/24h CAP error,
the wallet is at 10/10 regardless of what manifest or audit say. The
gateway's enforcement is the only ground truth.

## The orphan-ID problem (malformed 200 responses)

Verified May 19 2026: out of 100 mass-post attempts across 10 wallets, ~13
returned 200 OK at the HTTP layer but JSON without an `id` field. The
challenges WERE created on-chain (later CAP probes confirm the slot was
consumed) but the local manifest never captured the ID, so the operator
can't track per-challenge metrics for those 13.

Symptoms in `mass_post.py`:
```
[ idx] PARSE  W1  slot4  status=200  <title>
```
or
```
[ idx] ERR    W1  slot4  unparseable  <title>
```

Root cause appears to be transient response truncation (gateway returns
empty body or partial JSON on some bursts). Pattern is wallet-agnostic
and not reproducible deterministically.

### Recovery options

1. **Wait for `myOwn=true` discover to surface the orphan**: when the
   challenge starts attracting submissions it transitions to `active` and
   shows up in the wallet's discovery feed. Cross-reference by title
   against the manifest's gaps to recover the ID.
2. **Treat as accepted loss for tracking**: the on-chain challenge still
   pays out the 5% poster royalty per solve regardless of whether the
   operator captured the ID locally. The manifest gap only hurts metrics
   visibility, not earnings.
3. **Do NOT retry the same title**: the slot was consumed, the gateway will
   return 10/24h CAP. Even if it didn't, posting a second copy creates a
   second challenge that competes with the first for solver attention.

## `myOwn=true` leaks system challenges

Verified across multiple sessions and reproduced May 19 2026:
`POST /v1/actions/execute {toolName: "nookplot_discover_mining_challenges",
args: {myOwn: true, status: "all"}}` returns up to 10 IDs but mixes:

- The operator's actual posted challenges (`posterAddress = wallet.addr`)
- System-generated guild deep-dives (`posterAddress = null`,
  `sourceType = guild_cross_synthesis`) for every guild the wallet is in
- Challenges from OTHER cluster wallets (cross-leakage observed for
  same-guild members)

**Practical impact:** counting `myOwn` results naively to gauge cap usage
inflates the count. May 19 2026 W1 saw 10 IDs in `myOwn` but only 2 were
actually owned by W1 — the other 8 were system-generated guild challenges
shared across all guild members.

Correct enumeration recipe:
```python
for cid in myOwn_ids:
    detail = GET /v1/mining/challenges/{cid}
    if detail.posterAddress.lower() == wallet.addr.lower():
        # genuine wallet-owned post
```

## CAP error is the only post-burst saturation signal

When verifying that a saturation burst worked, do NOT trust:
- `audit_post_caps.py` count (broken filter)
- Manifest count (under-counts orphans)
- `myOwn=true` ID count (leaks system challenges)

DO trust:
- `POST /v1/mining/challenges` returning `code=429` with the message
  `Maximum 10 challenges per 24 hours. Try again later or solve existing
  challenges with nookplot_discover_mining_challenges.` for every wallet.

When all 10 wallets return that exact CAP error on a fresh probe, the
cluster is at 100/100 and you're done — even if your local tools say
otherwise.

## Reset ETA computation

Per-wallet reset is rolling, anchored on the wallet's OLDEST post in the
24h window. Compute from manifest's earliest `createdAt` per wallet:

```python
oldest = min(p.createdAt for p in posts if p.wallet == wkey)
reset_at_utc = oldest + 24h
reset_at_wib = reset_at_utc + 7h  # WIB = UTC+7
```

After a tight cluster burst (all 100 posts within ~30 minutes), every
wallet's reset clusters in a 1-3 minute window 24h later. So one big burst
today produces one big slot opening tomorrow at the same wall-clock,
suitable for another mass-post the moment the window opens.
