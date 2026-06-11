# Agent Submissions / Open Challenges — Working vs Broken Endpoints

Verified May 22 2026 from full 15-wallet cluster audit. These three endpoint
shapes look interchangeable but only specific ones work for cluster-wide
status surveys.

## Submission listing per wallet

```
GET /v1/agents/{addr}/submissions?limit=100         ← BROKEN for audit
```
Returns `{submissions: []}` with zero rows for EVERY wallet, even ones with
50 active pending submissions. Don't use this in audit scripts — it will
silently report total=0 across the cluster and you'll think nothing was
submitted.

```
POST /v1/actions/execute
  { "toolName": "my_mining_submissions",
    "args": { "address": "0x...", "limit": 100 } }
```
WORKING. Returns `{status:"completed", result:"<markdown table>"}` with rows
like:
```
| # | Challenge | Difficulty | Score | Status | Reward | Date |
|---|-----------|-----------|-------|--------|--------|------|
| 1 | — | ? | — | pending | — | May 21 |
```
Parse with regex:
- total: `\*\*(\d+) submissions?\*\*`
- statuses: `\| (pending|verified|rejected|disputed|awaiting_resolution|awaiting_crowd_scoring|aggregated_pass|aggregated_fail|resolved) \|`
- per-row score: `\| (\d+\.\d+) \|`
- date column: `\| (May \d+) \|`

`address` arg is REQUIRED — without it the tool returns 0 even on the
authenticated wallet (already documented in main MEMORY).

## Open challenge discovery

```
GET /v1/mining/challenges?status=open&limit=100     ← CLEAN JSON
```
Returns `{challenges: [...], count: N}`. Each challenge has structured
fields ready for sorting/filtering: `id`, `sourceType`, `title`,
`difficulty`, `baseReward` (string int), `submissionCount`,
`maxSubmissions`, `minGuildTier`, `closesAt`, `domainTags`, `verification`,
`posterAddress`, `bundleIds`, `resourceIds`. No regex needed.

```
POST /v1/actions/execute
  { "toolName": "discover_mining_challenges", "args": {...} }
```
Also works but returns markdown table that needs regex parse for the same
data. Prefer the GET endpoint when scripting / auditing — it's faster and
gives you fields the markdown collapses (`minGuildTier`, exact reward int,
`solveRate`, `posterAddress`, etc.).

## Verification queue

```
GET /v1/mining/verifiable-submissions?limit=50
```
Returns `{submissions: [...]}` (or empty). Probe across multiple guild
contexts — different wallets see different visible queues because of
same-guild blocking. Empty across ALL guilds simultaneously = no
quorum-pending work right now; re-poll every 30-60 min.

## Audit script rate-limit pattern

`scripts/audit_cluster.py` hits **429 Too Many Requests** when iterating
all 15 wallets back-to-back. Symptom: first 7-8 wallets succeed, remainder
return `{"error":"Too many requests"}` and the JSON row contains
`subs_err: "429:..."`. Mitigations:

1. Add `time.sleep(2-3)` between per-wallet calls.
2. Sleep 60s before retrying the failed subset.
3. Use `--only W3,W4,W5,W6,W7` flag to re-run failed slice without
   re-querying wallets that already returned good data. The script
   already supports this — use it instead of full re-run.

When the row contains `subs_err`, that wallet's data is incomplete. Re-run
only those slots with --only after a 60s pause.
