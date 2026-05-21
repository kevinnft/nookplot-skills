# Fresh wallet day-1 blockers — May 18 2026

Confirmed empirically against W6 satoshi (Jetpack tier2, fresh on May 17 2026)
during a "maksimalkan wallet 6" session.

## Hard blockers (USER ACTION required)

### GitHub PAT gate (commits + lines = 10K raw blocked)

The commits + lines dimensions (cap 6250 + 3750 = 10000 raw) are ENTIRELY
gated behind `POST /v1/github/connect` which requires a Personal Access Token:

```
POST /v1/github/connect
{"pat": "ghp_..."}
```

Without GitHub connection:
- `POST /v1/projects/:id/commit` → `403 GitHub not connected`
- `GET /v1/projects/:id/files` → `403 GitHub not connected`
- `nookplot_commit_files` (actions/execute) → wrapper drops `files` array
  ("files array is required") regardless of GitHub state
- `POST /v1/prepare/commit` → 404 (endpoint does not exist)
- `POST /v1/prepare/version` → 404
- `POST /v1/prepare/project/:id/versions` → 404 (gateway docs list it but
  actual gateway v0.5.32 returns 404)
- `POST /v1/projects/:id/versions` → 410 Gone with prepareEndpoint hint that
  itself 404s

There is no off-chain or relay path to commits/lines without a connected PAT.
Verified by exhaustive probe May 18 2026.

**Implication:** commits + lines is ~30% of the day-1 single-wallet ceiling
and is USER-ACTION blocked. When user says "maksimalkan wallet N" then
"sudah maks?" on a fresh wallet, state this up-front: those 10K raw points
require a GitHub PAT from the user. Don't probe variants — they all 404.

When a wallet already shows commits>0 (like W2 with commits=6250 from a prior
session), that wallet had a PAT connected previously and the connection
persists per-wallet on the gateway side.

### Bundle ContentIndex authorship (launches = 1.25K blocked)

`POST /v1/prepare/bundle` returns `CONTRIBUTOR_NOT_AUTHOR` even after
calling `/v1/memory/publish` with `{title, body, tags, domain}` and getting
back a CID. The on-chain ContentIndex anchor is async — fresh CIDs aren't
queryable as "authored by X" until ~10-30 min later.

The `prepare/memory/publish` and `prepare/content-index` endpoints don't
exist (404). The only working `/v1/memory/publish` shape is
`{title, body, tags, domain}` (returns CID); passing `{cid, ...}` to
post-hoc anchor an existing CID returns `400 title is required (string)`
on every variant tested.

**Workaround:** publish CIDs in session N, attempt bundle creation in
session N+1 (10+ min later). For single-session maximization, launches dim
stays at 0.

## Soft blockers (settlement lag, NOT user-blocked)

### Score breakdown freshness

`/v1/contributions/{addr}` `computedAt` advances every 5 minutes wall-clock
(xx:00, xx:05, xx:10, xx:15) but the underlying score-compute job runs every
~15 min on a separate cron. Content + social dims often lag 30-60+ min behind
activity even after `computedAt` updates.

For a fresh wallet doing a single-session push, expect:
- collab + citations (off-chain, fast indexing): visible within 5-10 min
- content (KG items, insights, memory/publish): visible within 30-60 min
- social (follows, endorsements, comments, channel posts, DMs): visible
  within 1-2 hours
- projects (prepare/project + relay): visible within 30-60 min
- marketplace (bounty applications): visible within 30 min

Don't read 0 in the breakdown as failure if the API confirmed the action
landed. `/v1/insights?author={addr}` returning 50 is ground truth that
content dim should fill — it just hasn't ticked yet.

## Platform-wide structural zeros

### `exec` dimension stays 0 for almost every wallet

Confirmed across W1 (rank 1, score 39519), W4 (commits=6225, projects=5000),
and the broader leaderboard top-200: `exec` is 0 for nearly every wallet.
W2 is the only exception observed (exec=554) and the mechanism for that 554
isn't surfaced in any documented endpoint. Treat exec as structurally
unreachable on day 1.

### `bundles` always 0 unless ContentIndex anchoring completes

See above. The leaderboard schema includes a `bundles` field that's always 0
even for top wallets — the launch dim is the same gate.

## Day-1 ceiling math (single-wallet, no PAT)

Maximum reachable in one session for a wallet without GitHub PAT:

```
collab        5000   ← off-chain, fast
citations     3750   ← off-chain, fast
content       4500-5000  ← settles 30-60 min after KG/insight push
social        2000-2500  ← settles 1-2h after follow/endorse/comment push
projects      2000-3500  ← settles 30-60 min, depends on relay budget
marketplace    800-1250  ← bounty apps, settles 30 min
TOTAL RAW     18-21K
× velocity 1.1-1.3 → 20-27K leaderboard score
```

With GitHub PAT connected:
```
above + commits 6250 + lines 3750 = +10000 raw → +11-13K score
TOTAL with PAT: 30-40K (matches W1 hermes day-N ceiling)
```

## Recovery / continuation prompts to user

When honest audit shows blocked dims and user asks "sudah maks?":
1. List the dims at MAX with green ✅
2. List dims pending settlement with ⏳ + projected timeline
3. List USER-ACTION blockers with ❌ + concrete ask:
   - "GitHub PAT untuk commits/lines: paste ghp_... atau aku skip"
   - "Launches butuh tunggu 10-30 min lalu retry — atau skip"
4. Give the day-1 ceiling number (18-21K raw without PAT, 28-30K with) so
   the user calibrates expectations against the 35K theoretical max.

Don't say "sudah maksimal" when commits/lines/launches are 0 by user-action
gates — that's a lie. Say "maksimal di lever yang viable tanpa PAT, sisa X
butuh user action."
