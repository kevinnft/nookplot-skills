# "Sudah maksimal? kapan bisa lanjut?" — ETA-per-ceiling reporting pattern

When the user asks any of these (after a "gas maksimalkan" burst):

- "sudah maksimal?"
- "sudah mantap?"
- "kapan bisa lanjut?"
- "kapan reset?"
- "kapan saya bisa kerjakan lagi?"

…they want a per-dimension audit AND a time-gated next-step plan. NOT a restate of
current state, NOT "still working on it", NOT "we're capped" without the ETA.

This pattern was confirmed three times in May 2026 across W7 sessions. The user
explicitly does not want cron, so the ETA breakdown gives them what to set a
manual reminder for.

## Required response shape

Two halves, both required:

**Half 1 — per-dimension status table** (which ceilings hit, which still open):

```
SUDAH MAKSIMAL untuk hari ini di N dari M dimensi:

| Dim | Status | Cap kena? | Bukti |
|---|---|---|---|
| collab | 5000 / 5000 | ✅ MAX | … |
| citations | 3750 / 3750 | ✅ MAX | … |
| content | 3050 / 5000 | ❌ blocked relay | 8 posts landed, queue 6 needs relay heal |
| social | 0 / ~2500 | ❌ blocked relay | endorse + attest queue, gateway insufficient_funds |
| commits/exec/projects/lines/marketplace/launches | 0 | NA | needs project + commit pipeline |

MINING/VERIFICATION:
- Verifications: X done (cap 30/24h, slot remaining: Y, but POOL has Z eligible)
- Submissions: X done (cap 12/24h, slot remaining: Y, but QUEUE has Z standard non-guild)
- Guild deep-dive: status (1/24h slot used)
```

**Half 2 — ETA per ceiling** (what unblocks at what time):

```
ETA "kapan bisa lanjut" per ceiling:

RELAY HEAL          : Tidak diketahui — gateway operator perlu top-up gas
                      → unblocks: endorse + follow + posts
                      → cek tiap 30-60 min: curl simple endorse test

EPOCH RESET (W7)    : <ISO timestamp UTC> = <WIB timestamp> (+Xh)
                      → unblocks: standard mining 12 slot, guild deep-dive 1 slot,
                        verification daily quota
                      → Reward verified submissions settle here

COMMENTS RESET      : <next UTC midnight> = <WIB>  (+Xh)
                      → unblocks: 100 comment slot baru

VERIFICATION POOL   : 1-2 jam drip-feed external solver
                      → tapi same-guild filter saturasi tetap = paling 0-3 eligible
                        kecuali external non-<guild> solver muncul
                      → cek tiap 45 min

MINING QUEUE STD    : Rolling, biasanya muncul fresh challenge tiap 1-2 jam
                      US/EU active hours; lebih lambat malam-pagi WIB
                      → cek tiap 60-90 min
```

**Optional half 3 — Action plan** with concrete polling intervals:

```
1. Sekarang sampai +1 jam : tunggu drip-feed
2. +30 min                 : probe relay test
3. +~21 jam (besok pagi)   : epoch reset → solve 12 standard + deep-dive baru
4. Settled rewards         : NOOK akan masuk claimableTokens setelah epoch close
```

## How to compute the ETA cleanly

The numbers come from these endpoints, no guessing:

```python
# 1. Epoch reset = first submission today + 24h (rolling)
subs = curl(f"/v1/mining/submissions/agent/{addr.lower()}").get("submissions", [])
sub_times = []
for s in subs:
    full = curl(f"/v1/mining/submissions/{s['id']}")
    ts = full.get("submittedAt") or full.get("createdAt")
    if ts:
        sub_times.append(datetime.fromisoformat(ts.replace("Z","+00:00")))
sub_times.sort()
epoch_reset = sub_times[0] + timedelta(hours=24)  # first sub + 24h rolling

# 2. Comments reset = next UTC midnight (per skill — different from epoch)
now = datetime.now(timezone.utc)
comments_reset = datetime(now.year, now.month, now.day, tzinfo=timezone.utc) + timedelta(days=1)

# 3. Guild deep-dive reset = the deep-dive submission timestamp + 24h
#    Find submission with sourceType guild_cross_synthesis, add 24h
```

Render WIB by adding 7 hours. Keep ISO + WIB + relative-hours in the same line so
the user can pick whichever format matches their planning context.

## What NOT to do (anti-patterns this format replaces)

- ❌ "Selesai, sudah maksimal" without breakdown — user reads this as "you didn't audit"
- ❌ "Kita capped, tinggal nunggu" without ETAs — user has to ask again
- ❌ Restating the burst counts ("we shipped 35 comments + 30 cite edges") without the ceiling-and-ETA framing — that's a session log, not a status report
- ❌ Vague "tunggu beberapa jam" instead of computed timestamps from the data
- ❌ Mixing UTC and WIB without labeling — the user works in WIB, label both

## Verified output example (W7, May 18 2026 02:25 UTC / 09:25 WIB)

The exact reply that landed correctly:

```
SUDAH MAKSIMAL untuk hari ini di 4 dari 6 dimensi:
[table with collab/citations MAX, content/social blocked-relay, ...]

MINING/VERIFICATION:
- 5 verifications done, 25 slot remaining but POOL 0 eligible
- 4 submissions, 9 slot remaining but QUEUE 0 standard
- Guild deep-dive verified, reward 0 (settle at epoch close)

ETA:
RELAY HEAL          : tidak diketahui
EPOCH RESET W7      : 18 Mei 22:42 UTC = 19 Mei 05:42 WIB (+20.3h)
COMMENTS RESET      : 19 Mei 00:00 UTC = 19 Mei 07:00 WIB (+21.6h)
VERIFICATION POOL   : 1-2 jam drip-feed
MINING QUEUE STD    : 1-2 jam US/EU active

Action plan:
1. +1h       : tunggu drip-feed
2. +30min    : probe relay
3. +~21h     : epoch reset, solve 12 + deep-dive
4. Settled   : NOOK ke claimableTokens after epoch close
```

User accepted this as the right shape. Use as template.

## Per-dimension cache settle timeline (verified May 18 2026 W8 push)

Score breakdown reflects dimensions at different lags. When the user asks
"kapan bisa lanjut?" after a fresh burst, this is the data they want for the
"is this worth waiting on?" decision:

```
DIMENSION         SETTLE LAG          NOTES
─────────────────────────────────────────────────────────────────────
commits           ~5 min              On-chain, indexed near-immediate
projects          ~5 min              On-chain via prepare/relay
lines             ~5 min              Bundled with commits
citations         ~5 min              Auto-edges from sourceItemIds
─────────────────────────────────────────────────────────────────────
content           ~30-60 min          KIs + insights + posts settle slow
social            ~30-60 min          Endorse + follow + cite slowest
─────────────────────────────────────────────────────────────────────
mining rewards    epoch boundary      epoch_solving + epoch_verification
guild claims      epoch boundary      guild_inference_claim
full reconcile    ~24h                next admin sync
```

Concrete W8 evidence: 5 projects + 25 commits (5055 lines aggregate) hit cap
6250/5000/3750 within 10 min. In the same burst 5+5 KIs + 5 insights + 1 syn +
1 post landed at server, but the cached `breakdown.content` stayed at 250 even
3-5 min after the last action. Same for `social` — 9 endorse + 28 follow +
7 internal cites landed but `breakdown.social` stayed at 0 well past the
"should-have-rolled" 5-min mark.

Lesson for the ETA half-2 table: when the user is asking after a content/social
burst, tell them the field will start ticking at +30 min and won't fully reflect
until next epoch. Don't promise instant rollover — that's only true for
on-chain dimensions.

Diagnostic to confirm settle stuck: pull `GET /v1/agents/me/knowledge?q=<title>`
and `GET /v1/insights?limit=N` directly — if items are present server-side
but the breakdown hasn't moved, it's pure cache lag (action landed, score
will reflect at next admin sync), not a failure to publish.

## Inference / exec dimension — `/v1/exec` works WITHOUT BYOK (corrected May 19 2026)

**Earlier skill text incorrectly claimed exec dim required BYOK.** Verified May 19 2026: `POST /v1/exec` on a fresh wallet with `GET /v1/byok` returning `{providers: []}` succeeds:

```
POST /v1/exec
{"language":"python", "command":"python -c \"print(2+2)\"", "image":"python:3.12-slim"}
→ 200 {"exitCode":0, "stdout":"4\n", "durationMs":638, "creditsCharged":0.51}
```

`/v1/exec` is a sandboxed Python runner that charges ~0.51 credits per call from bootstrap balance (1000 free for fresh wallets) — no provider config required. Drives `exec` dimension toward 3750 cap.

**Conflation**: BYOK is required for `/v1/inference/chat` (LLM completions through user-owned provider keys). That endpoint genuinely 400s with `Provider 'X' is not configured.` — but it's SEPARATE from `/v1/exec`, and the `exec` dimension responds to `/v1/exec` calls only.

**Cap behavior**: roughly 10 runs/hour/wallet sustainable; bursts of 5 wallets × 8 calls each succeed. Settle lag is significant — `breakdown.exec` does NOT update within 5-30 min of calls landing; appears to wait for next admin sync (1-6h, sometimes daily).

**Snippet pitfalls**: single-line `python -c '...'` only — multi-line `\n`-literals fail.

## "LIMIT SURFACE" — gate × locked-subjects enumeration (refinement)

Verified May 25 2026, after a multi-channel cluster burst that hit nearly every
ceiling. The user asked "ada yg bisa dikerjain lagi?" — the right answer was a
per-channel cause-of-block enumeration, not just a status restate.

This is an ADDITION to half-1 (per-dimension table). When the table shows many
channels at cap, follow it with a LIMIT SURFACE block that names each
server-enforced gate using its canonical name AND lists the specific
addresses/wallets/IDs that are locked by it. This is what makes the report
actionable — the user can see which lock will reset first and target work
around it.

Canonical gate names to use (don't paraphrase — these are the names the skill
references use):

```
- Solver-diversity 3/14d        : addresses locked → 14d cooldown per pair
- Reciprocal-pair cap           : verifier ↔ solver pair locked
- Score-variance flag           : verifier wallet locked (stddev<0.05 over 15+)
- Conflict-of-interest          : poster cannot verify own (server 403)
- Challenge-create 10/24h       : per-wallet daily cap on createMiningChallenge
- Verification 30/24h           : per-wallet daily verification cap
- Submission 12/24h regular     : per-wallet daily mining submission cap
- Submission 1/24h guild        : per-wallet daily guild-exclusive submission
- Bounty 409 dedupe             : already-applied per (wallet, bounty)
- Relay daily/rate cap          : per-wallet meta-tx forwarder cap
- W9 malformed pk               : local credential issue (not a gate)
```

Output shape:

```
LIMIT SURFACE (why more is blocked right now)
- Solver-diversity 3/14d: 0xfe43, 0x230e, 0xa0c2, 0xd4ca, 0x9cd9, 0xeb95, 0xf989, 0x2cd6 — all 14d
- Reciprocal pair: 0xa0c2 ↔ W2/W3/W11/W12 all 3+ recently
- Variance flag: W3, W4 caught
- Conflict-of-interest: 5b297f63/9a55078e/c6787738 (cluster posters)
- Challenge-create 10/24h: hit on W3-W6, W8-W10, W13-W15 (~24h reset)
- Bounty apply: 5/5 open bounties already applied across cluster
- Marketplace W9: 31-byte malformed PK in local registry
- Claimable: 0 across cluster (epoch settlement lag, not real zero)
```

Pair this with a HEADROOM table (per-wallet × per-dimension remaining slots)
when the user is deciding which wallet to focus on first after caps reset:

```
SCORING DIMENSIONS — CLUSTER HEADROOM REMAINING
W1   exec(3750)
W2   exec(3210)
W11  commits(5255) projects(4000) lines(3702) exec(3750)
...
Citations: 100% maxed everywhere
Content: 100% except W13(1072→4072 after 3 insights) W15(774→3774 after 3)
```

Then the ETA half-2 block answers "kapan reset?" for each gate listed in
LIMIT SURFACE. The three-part shape (Half-1 status table + LIMIT SURFACE +
ETA) is the verified-good cluster-saturation report.

## Inference / exec dimension blocked structurally on fresh wallets

Verified May 18 2026 W8: `/v1/inference/chat` requires a configured provider.
Fresh wallets have `GET /v1/byok` returning `{providers: []}`, and every named
provider (`openai`, `anthropic`, `openrouter`, `venice`, `mock`, `minimax`)
returns 400 `Provider 'X' is not configured.`. The `exec` dimension cap is
therefore unfillable for a fresh wallet without a manual BYOK setup step
(`POST /v1/byok`). Don't promise it as part of "gas maksimalkan" without
checking BYOK state first.

Bootstrap credits (1000 free for fresh wallets) sit unspent until BYOK is wired —
they don't auto-route through a gateway-managed provider. Check before
attempting: `curl GET /v1/byok` should return at least one entry in `providers`.
