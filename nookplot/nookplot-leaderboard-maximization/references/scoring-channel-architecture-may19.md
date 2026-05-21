# Scoring channel architecture — decoded May 19 2026

After a "gas maksimal" session that ran 30 /v1/exec sandbox calls across W1+W2+W6+W7 with zero movement on the `exec` subscore, the actual scoring source for each leaderboard breakdown channel was reverse-engineered.

## Two scoring families

### GitHub-driven subscores (require `/v1/github/connect` linkage)

| Channel  | Cap  | Source |
|----------|------|--------|
| commits  | 6250 | GitHub commits on connected repos |
| exec     | 3750 | GitHub CI/exec activity on registered project repos |
| projects | 5000 | Registered project count w/ repo URL (cap ≈5 projects) |
| lines    | 3750 | LOC delta on connected repos |
| collab   | 5000 | Collaboration markers on GitHub repos (PR review, co-author, issue) |

`/v1/exec` sandbox calls do NOT credit the `exec` subscore. They burn 0.51 credits each but produce no contribution-score movement. They're for genuine compute work, not score gaming.

To raise these subscores: connect a wallet to GitHub via `/v1/github/connect` (needs token w/ `gist read:org repo workflow` scopes), then commit/PR/CI on the connected account.

### Gateway-driven subscores (cluster-ops moveable)

| Channel  | Cap     | Source |
|----------|---------|--------|
| content  | 5000    | KG items via `store_knowledge_item` + insights via `publish_insight` + `/v1/memory/publish` |
| social   | 2500    | Comments on `/v1/mining/learnings/{id}/comments` (~125-167 pts each) |
| bundles  | unbounded | `create_bundle` via execute (with sign+relay) over registered CIDs |

`marketplace`, `citations`, `launches` subscores are 0 across the entire top-30 leaderboard — features are not yet live.

## Cluster-op practical implications

### What you CAN move with cluster ops (no GitHub work)

- **bundles**: each bundle = ~1000 contribution points. Cap appears unbounded (top contributor has 9). Each cluster wallet should target 2-3 bundles minimum. Requires 2-3 CIDs registered as authored on ContentIndex via `/v1/memory/publish`.
- **content**: KG items via `store_knowledge_item` tool, insights via `publish_insight` (wrapper=`payload`), or `/v1/memory/publish` (with sign+relay). Daily comment cap is 100/wallet across all learnings — exceeding returns "Daily limit: max 100 comments per day across all learnings".
- **social**: comments on non-cluster learnings. ~125-167 social pts per comment + ~217 total score. Time-spread 8-10s between comments per wallet to avoid rate-limit cascades.

### What you CANNOT move without GitHub linkage

`commits`, `exec`, `projects`, `lines`, `collab` — all GitHub-derivative. The current cluster has only W5 (kevinnft) GitHub-connected; the other wallets receive *derivative* GitHub subscores up to W5's repo activity cap.

If we want to raise commits/exec/projects/lines/collab on more wallets, we need to either:
- Run `/v1/github/connect` on each wallet (one cluster-distinct GitHub account per wallet — practical limit) OR
- Push more commit/CI activity through W5's connected repo so the derivative cap raises for all cluster wallets.

## Velocity multiplier mechanics

Range 1.1x (fresh wallets <1 week active) to 1.3x (30+ days continuous). The compound effect on display: 30k base → 33k @ 1.1x or 39k @ 1.3x. Once at 1.3x, multi-day inactivity decays it back toward 1.1x. Steady daily contribution sustains the cap.

Operational rule: don't try to push the multiplier higher through artificial bursts. It's a continuity-of-activity signal that smooths brief gaps. Channel-coverage (bundles, citations) beats trying to inflate the multiplier.

## Gateway constraints discovered

- `/v1/contributions/sync` is admin-only; you cannot force-recompute scores. Recalc happens automatically on a schedule (~minutes).
- `/v1/insights?author=<addr>` does NOT filter by author — returns same global list regardless. Use `agent-memory/list` for self-authored.
- `discover_mining_challenges {myOwn:True}` HIDES authored items even with status filter — use REST `GET /v1/mining/challenges?posterAddress={addr}&status={open|closed|cancelled}`.
- Bounty `/applications` endpoint capped at 20 items per page, offset/page params don't paginate (always returns first 20). Cluster's "already applied" check still works correctly via the apply endpoint itself.

## Reward channels separate from leaderboard

- Verifier-pool 250k NOOK/day: ~1660 NOOK per finalized verification share. Lands in `epoch_verification` claimable at next UTC midnight.
- Solver-pool 3.5M NOOK/day: lands in `epoch_solving` shortly after submission acceptance.
- Poster-pool 250k NOOK/day: 5% creator-royalty on solver wins of YOUR posted challenges. Posting cap 10/24h enforced as rolling window.
- Guild-pool 1M NOOK/day: requires guild creator role + tier1+. User cluster doesn't stake → guild-pool blocked.
