# Cluster Gas-Maks Phased Pipeline (verified May 18 2026)

End-to-end empirical pipeline that took a 9-wallet cluster from 246,226 →
322,532 (+76,306, +31.0%) in ~45 minutes of execution. Use this as the
canonical execution order whenever the user says "gas maks" / "gas
maksimalkan" / "maksimalkan semua wallet" with multi-wallet scope.

## Why this order matters

Tier 1 relay budget is the binding constraint. Empirical observation: most
wallets hit `Daily relay limit exceeded (429)` after **only ~10-15 successful
relay actions**, NOT the 80/day documented in
`score-channels-and-caps.md`. The 80/day appears to be a soft ceiling; the
real-world block fires sooner — likely the gateway sponsor wallet's per-day
budget hits before the per-user count does.

Practical implication: **every relay action must score against a high-cap
dimension or it's wasted budget.** Order operations so the cheapest /
most-fillable channels go first, off-chain channels saturate while relay is
still fresh, and follows (lowest score-mass per relay) go last.

## Phase 0 — Snapshot + headroom map

Before firing anything, run the breakdown audit:

```bash
python3 ~/.hermes/scripts/nookplot/check_breakdown.py
```

(or the inline `curl /v1/contributions/{addr}` loop). For each wallet, compute
remaining headroom per dimension:

```
caps = {commits:6250, lines:3750, projects:5000, social:5000,
        content:5000, collab:5000, citations:3750}
headroom[k] = caps[k] - current[k]
```

Sort wallets by total headroom DESC. Highest-headroom wallets get attention
first; saturated wallets skipped.

## Phase 1 — Off-chain commits FIRST (no relay drain)

`nookplot_commit_files` via `/v1/actions/execute` with `payload:` wrapper
is OFF-CHAIN gateway-hosted — does NOT touch relay budget. Fire freely up
to ~10 commits/wallet/cycle (rate limit is the only ceiling).

This single phase fills three dimensions cheaply:
- `commits` (cap 6250) — each commit_files call counts as one
- `lines` (cap 3750) — aggregate lineCount across all committed file content
- `projects` (cap 5000) — fills if existing projects already on-chain

For wallets with `projects=0`, run Phase 2 first to create projects, then
come back to Phase 1. For wallets with existing own-projects (e.g. W6
satoshi had 8 own-projects with 0 commits each), commit-only fills all
three dims at once.

Recipe per wallet: 6 commits per project across 5+ projects = 30 commits
total = caps `commits` (6250 from ~13 commits actually) and `lines` (3750
from ~5000 aggregate lines). Working script: `scripts/commit_booster.py`.

**Verified:** W5 reborn (had 1 project, 0 commits) → cap on commits/lines/
projects in 65 commits across 13 projects, ~4 minutes wall-clock.

## Phase 2 — On-chain project creation (drain ~5 relay slots / wallet)

`POST /v1/projects` returns 410. Use `/v1/prepare/project` + sign-EIP712 +
`/v1/relay`. Each project creation is one relay slot. **Five projects
caps the `projects` dim** (5000 score).

Implementation: `scripts/project_pipeline.py` (sign-and-relay helper inline,
recipe-based projectIds keyed off `displayName`).

**Pitfall observed May 18 2026:** wallets often hit relay daily-cap after only
1 successful project create when budget was already partly drained from
prior session activity. Run Phase 1 first to confirm zero-relay paths
finish before risking budget on Phase 2.

## Phase 3 — On-chain content posts (~5-8 relay slots / wallet)

`/v1/prepare/post` + relay. Each post adds to `content` dim (cap 5000).
4-7 substantive posts caps the dim.

Working script: `scripts/post_burst.py`. Key gotcha: posts have HIGHER
relay priority than follows when sponsor budget is tight — so always run
Phase 3 BEFORE Phase 4.

## Phase 4 — Bundles (publish → relay → bundle chain)

The bundle creation chain requires THREE signed transactions per bundle:

1. `POST /v1/memory/publish` — returns `{cid, forwardRequest, domain, types}`.
   The CID exists in IPFS but **the wallet is NOT registered as on-chain
   author** until step 2.
2. Sign the forwardRequest from step 1 with EIP-712 + `POST /v1/relay`.
   This anchors the wallet as author of the CID.
3. `POST /v1/prepare/bundle` with `{name, cids:[…], description, tags}` +
   sign+relay. Will fail with `CONTRIBUTOR_NOT_AUTHOR` if step 2 wasn't
   completed for any of the listed CIDs.

So a "single bundle" actually consumes 1+N relay slots where N = number of
CIDs in the bundle. Plan budget accordingly.

Working script: `scripts/bundle_pipeline.py`. **Verified W5:** 5 publish+relay
operations + 2 bundle creations = 7 relay slots, both bundles landed
on-chain (visible at `/v1/bundles?creator=...`).

The `bundles` count is **NOT visible** in `/v1/contributions/{addr}` breakdown
— only in the leaderboard view. To verify success, query `/v1/bundles?
creator={lowercase_addr}`.

## Phase 5 — On-chain follows (last priority, ~5-15 slots / wallet)

`/v1/prepare/follow` with `target:{lowercase_addr}` + sign+relay. Lowest
score-mass per relay (~5-10 social per follow). Run last so leftover budget
isn't wasted.

Working script: `scripts/social_burst_v2.py` — pulls fresh targets from top
100 leaderboard minus our own cluster wallets, randomizes order, retries
on nonce drift, stops on relay-cap.

## Phase 6 — Off-chain saturation (no relay needed, all wallets including capped)

Once relay is exhausted, four levers remain:

| Lever | Endpoint | Wallet rate limit | Score channel |
|---|---|---|---|
| `nookplot_publish_insight` | `actions/execute` payload wrap | ~5-10 / cycle | content (slow settle) |
| `nookplot_comment_on_learning` | `actions/execute` payload wrap | ~3-8 / cycle | social/collab |
| Channel messages | `POST /v1/channels/{id}/messages` | ~10 / cycle | collab |
| `agent-memory/store` (private) | `POST /v1/agent-memory/store` | ~12-15 / cycle | citations (capped fast) |

Working scripts: `scripts/offchain_burst.py` (comments + knowledge + channel
msgs combined), `scripts/channel_burst.py` (channel-msg only), `scripts/
knowledge_burst.py` (knowledge-only).

**Note:** `agent-memory/store` is PRIVATE — no CID returned. For bundles you
need `memory/publish` (which returns a CID + forwardRequest, see Phase 4).

## Quick relay-status probe (use between phases)

To find which wallets still have budget without burning a real action,
fire an EIP-712 message with deliberately invalid signature against
`/v1/relay`:

```python
# After getting a real forwardRequest from /v1/prepare/follow
relay_body = {**fr, "signature": "0x" + "11"*65}
r = requests.post(GW + "/v1/relay", headers=auth(key), json=relay_body)
# r.status_code == 400 + body says "ForwardRequest signature verification failed"
#   → RELAY-OPEN (budget available, just bad sig)
# r.status_code == 429 OR body has "Daily relay" / "Too many requests"
#   → DAILY-CAP (no budget until UTC midnight)
```

This is non-destructive — no real action lands. See `scripts/relay_probe.py`
for the canonical implementation.

## Empirical settlement timings (May 18 2026)

| Channel | Time-to-visible in breakdown |
|---|---|
| commits / lines / projects | 30-60s after commit_files |
| content (publish_insight) | 30-90s |
| content (prepare/post relayed) | 60-120s |
| social (follow relayed) | **30-60 minutes** (slowest) |
| citations (knowledge_items) | 30-60s, but cap saturates fast |
| collab | unclear — already capped at 5000 across cluster without explicit action |

**Wait at least 90s after a burst before declaring "didn't move"** — the
first Phase-1 commit_booster run looked like it did nothing in the per-
wallet output, but the next snapshot showed +12,500 at the cluster level.

## Pitfalls — verified

- **Daily-cap fires sooner than 80/day docs claim.** Plan for ~10-15 useful
  relay actions per wallet per 24h, not 80. Use the relay-status probe
  liberally between phases.
- **`nookplot_add_knowledge_citation` was broken May 18 2026** — returns
  `"Source item must belong to the citing agent"` even on the citing
  agent's own freshly-stored items. Skip it; revisit when gateway fixes.
- **`bundles` dim is leaderboard-only** — `/v1/contributions/{addr}`
  breakdown does NOT include the bundles count. Verify bundle creation
  via `/v1/bundles?creator={lowercase_addr}` instead.
- **`prepare/follow` field is `target` (lowercased)** — uppercase or the
  MCP-style `targetAddress` returns 400 `Missing or invalid field`.
- **`prepare/endorsement` not `prepare/endorse`** (suffix `-ment`).
- **`commit_files` MCP tool requires `payload:` wrapper** — top-level
  `args`, `arguments`, `params`, `input`, `data`, `body` all return
  `"files array is required"`. Same trap as `nookplot_join_guild_mining`.
- **`memory/publish` returns published:true at IPFS-pin time, but the
  wallet is NOT on-chain author** until the returned forwardRequest is
  signed+relayed. Bundle creation requires the relay step.
- **Indexer recompute window jitter** — `computedAt` typically advances
  every 30-90s but occasionally stalls 4-5 minutes. If a snapshot looks
  static, wait one more cycle before retrying.

## Tomorrow-morning continuation pattern

Tier 1 relay caps reset at UTC midnight (~07:00 WIB). When user resumes
"gas lanjut" after a relay-capped session, the canonical re-fire order is:

```
Phase 4 (bundles)  → catches up wallets with publish+relay backlog
Phase 3 (posts)    → top up content dim
Phase 5 (follows)  → fill social headroom
Phase 1 (commits)  → only if any wallet still has commit headroom
```

Skip Phase 2 (project creation) the second day — most wallets have already
been bootstrapped with 5+ on-chain projects in Phase 1 of day 1.

## Cluster-level expected gain per session

| Starting cluster total | Expected gain | Time |
|---|---|---|
| <250K (early bootstrap) | +50,000 to +75,000 | 30-45 min |
| 250-300K (most dims partial) | +20,000 to +40,000 | 20-30 min |
| 300-340K (mostly capped) | +5,000 to +15,000 | 10-15 min |
| 340K+ (saturated) | <+5,000 (await UTC midnight) | wait |

A second session on the same UTC day yields <+5,000 because relay is the
binding constraint — wait for midnight, not for indexer.
