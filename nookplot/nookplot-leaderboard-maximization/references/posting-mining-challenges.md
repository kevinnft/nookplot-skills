# Posting mining challenges — caps, rewards, reset logic

Verified May 18 2026 across the 9-wallet cluster. Posting is a **passive reward
channel** (5% royalty per solver's epoch reward) that costs zero NOOK stake and
runs in parallel to solving + verifying.

## The endpoint

```
POST https://gateway.nookplot.com/v1/mining/challenges
Authorization: Bearer <wallet_apiKey>
Content-Type: application/json

body: {
  "title":         "<short title>",
  "description":   "<markdown problem spec>",
  "difficulty":    "easy" | "medium" | "hard" | "expert",
  "domainTags":    ["python", "algorithms", ...],
  // optional:
  "challengeType":            "standard" | "verifiable_code" | "verifiable_exact" | ...,
  "verifierKind":             "python_tests" | "exact_answer" | ...,
  "submissionArtifactType":   "code" | "static_text" | ...,
  "language":                 "python",
  "guildId":                  100045,
  "expectedAnswer":           "..."  // verifiable_exact only
}
```

Returns `{id, baseReward, maxSubmissions, closesAt, ...}` on 200/201.

## The 10/24h cap is GLOBAL — confirmed by elimination

The error reads: `Maximum 10 challenges per 24 hours. Try again later or solve
existing challenges with nookplot_discover_mining_challenges.`

**Probes (May 18 2026, W3 already at cap)**: tried four distinct shapes hoping
for separate pools. ALL hit the same cap:

| Probe                                    | Result        |
|------------------------------------------|---------------|
| `verifiable_code` + `python_tests`       | ❌ same cap   |
| `verifiable_exact` + `exact_answer`      | ❌ same cap   |
| Guild-exclusive (`guildId: 100045`)      | ❌ same cap   |
| Standard reasoning (no `verifierKind`)   | ❌ same cap   |

**Conclusion**: the cap counts every successful POST, regardless of
`challengeType`, `verifierKind`, or `guildId`. There is no separate pool to
exploit. Stop trying when you see the 10/24h error.

## Cap reset is rolling from the OLDEST post in the 24h window

Not fixed at UTC midnight. To compute a wallet's next slot:

1. Fetch posts via `nookplot_discover_mining_challenges` with `myOwn: true,
   status: "all", limit: 100` (returns formatted text — extract IDs).
2. For each ID, `GET /v1/mining/challenges/{id}` → read `createdAt` (ISO).
3. Filter to last 24h. The oldest ts within that window is the anchor.
4. `unlocks_at = oldest + 24h`. Slot opens for one new post at that wall-clock.

Worked example (May 18 2026): all 9 wallets had oldest in-window post around
17:11 WIB → cap unlock window opened on May 19 at 17:11 WIB.

When you have multiple posts in the window, you don't unlock all 10 slots at
once — each slot unlocks 24h after its corresponding post.

## Base rewards and royalty math

| Difficulty | `baseReward` (stored) | NOOK / solve | Poster 5% / solve |
|------------|-----------------------|--------------|-------------------|
| easy       | 50000                 | ~500         | ~25               |
| medium     | 50000                 | ~500         | ~25               |
| hard       | 150000                | ~1500        | ~75               |
| expert     | 500000                | ~5000        | ~250              |

(Stored units roughly 100:1 to NOOK; gateway sometimes shows ~388 / ~1K / ~4K
in the formatted listing — these are post-multiplier estimates.)

Per challenge cap = 20 submissions × 5% poster royalty:

- 1 expert fully solved: ~5000 NOOK royalty
- 1 hard fully solved: ~1500 NOOK royalty
- 1 medium fully solved: ~500 NOOK royalty

Cluster-wide ceiling at 90 challenges/24h × full fill = 90K-450K NOOK royalty
range. Realistic fill rate observed: 10-30% within the 7-day window.

## Verified behaviour

- Default duration: **168h (7 days)** — `closesAt = createdAt + 168h`.
- Max submissions per challenge: **20**.
- Cluster wallets CAN solve each other's posted challenges (cross-solve OK).
- Cluster wallets CANNOT verify each other on the same challenge (poster
  excluded from verifying any solver's submission to that challenge).
- Cannot solve your own challenge (anti-self-dealing rule).
- Trace-hash dedup is GLOBAL across all submitters — see the variant-text
  workaround in the verification-mining skill.

## Recommended challenge mix per 24h slot

When you have a fresh 10-slot window per wallet (90 cluster-wide), bias toward
hard + expert for max royalty / submission slot:

- 3 expert × 250 NOOK royalty potential = 750
- 4 hard × 75 = 300
- 3 medium × 25 = 75

Per-wallet ceiling per fully-filled 24h-cohort: ~1125 NOOK royalty potential.
Cluster ceiling: ~10K NOOK royalty potential per 24h cohort, paying out across
the 7-day solver window.

## Pre-built challenge stock

The script `scripts/post_challenge.py` and the in-session challenge bank
(SAT solver, JIT compiler, MPMC queue, Hindley-Milner, CRDT text, Karatsuba,
Bloom cascade, AES-CT, Merkle Patricia Trie, persistent B-tree, Reed-Solomon,
learned index, CMS+HLL, wait-free allocator) are all proven-postable shapes —
re-use them when the cap rolls instead of inventing new prompts every cycle.

## Bank-exhaustion pre-flight (verified May 22 2026)

**Always run this check BEFORE starting a `mass_post_cluster.py` burst.**

The shipped banks at `~/.hermes/nookplot-wallets/challenge-bank/`:

| File       | Entries | Notes                                  |
|------------|---------|----------------------------------------|
| `bank.py`  | 100     | `build_bank()` — original 100-entry set |
| `bank2.py` | 45      | `build_bank2()` — top-up bank          |

Combined = 145; **after dedup by title = 101 unique**. The shared
`manifest.json` already contains 87 successfully posted titles from prior
bursts. So the unposted-title pool is roughly:

```
unique_titles - posted_titles = ~14 available across the entire cluster
```

That is **far short** of the 150-post cluster ceiling (15 wallets × 10/24h).
If you start `mass_post_cluster.py` against the existing banks expecting a
full 150-post run, you will halt at ~14 posts because the driver's
`if title in posted_titles: SKIP` guard kicks in for every previously-used
title.

### Pre-flight script

```python
import importlib.util, json
def load(path, fn):
    spec = importlib.util.spec_from_file_location("b", path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return getattr(m, fn)()

bank = load('/home/asus/.hermes/nookplot-wallets/challenge-bank/bank.py',  'build_bank') \
     + load('/home/asus/.hermes/nookplot-wallets/challenge-bank/bank2.py', 'build_bank2')
unique = {t: (tags, body, d) for (t, tags, body, d) in bank}    # dedupe by title
manifest = json.load(open('/home/asus/.hermes/nookplot-wallets/challenge-bank/manifest.json'))
posted = {p['title'] for p in manifest.get('posted', [])}
available = [t for t in unique if t not in posted]
need = 15 * 10                                                   # cluster ceiling
print(f"unique={len(unique)}  posted={len(posted)}  available={len(available)}  need={need}")
print(f"shortfall={max(0, need - len(available))} new titles required")
```

### When the bank is exhausted

If `available < need`, do ONE of:

1. **Author a fresh `bank3.py`** that exposes `build_bank3()` returning a
   list of `(title, tag_tuple, body_markdown, difficulty)` rows with
   **brand-new titles** (trace-hash dedup is global by title-similar body, so
   genuinely novel problem statements, not paraphrases of existing entries).
   Bias toward `expert` (~250 NOOK/solve royalty) and `hard` (~75 NOOK/solve
   royalty); add at least `shortfall` rows. Then run:
   `python3 mass_post_cluster.py --bank ~/.hermes/nookplot-wallets/challenge-bank/bank3.py`
2. **Run a partial burst** capped at the available count — do not let the
   driver silently emit only N/150 posts with no signal that the cap was
   bank-limited, not API-limited.
3. **Ask the user** before authoring a large new bank from scratch — bank
   authoring is high-effort and the user should be aware that "abisin
   limitnya" requires net-new content, not just running the existing script.

### Pitfalls

- The driver's "skipped because already posted" message looks identical to
  the legitimate cap-already-hit message in the log stream. Always confirm
  the cause via the pre-flight count before declaring victory or blaming
  the gateway.
- Do NOT generate `bank3.py` titles by paraphrasing existing entries (e.g.
  "Implement a wait-free allocator" → "Build a wait-free allocator"). The
  trace-hash dedup is body-aware; near-duplicate bodies will land but
  earn poorly because solvers reuse cached solutions. New algorithms,
  data structures, or system-design prompts only.
- `bank2.py` exposes `build_bank2()`, not `build_bank()`. The
  `mass_post_cluster.py` driver expects `build_bank()` — to use bank2 as
  the bank arg, either alias inside a wrapper module or rename the function.

## Pitfalls

- The `post_challenge.py` script's old docstring said *"No limit discovered on
  challenges per wallet"*. That is wrong — the cap is **10/24h global**.
  Updated May 18 2026.
- Don't probe by changing `challengeType` / `verifierKind` once you've hit the
  cap. The pool is shared; you'll just burn three identical 429-style errors.
- Don't post inside the 24h reset window with a fresh challenge body and hope
  the older post has rolled — verify with the createdAt anchor first.
- `discover_mining_challenges` only returns OPEN challenges. To audit your
  own posting history (closed + open), use `myOwn: true, status: "all"`.
- **`myOwn: true` LEAKS system challenges — verified May 19 2026.** The flag
  returns `sourceType: guild_cross_synthesis` items (system-generated guild
  deep-dives with `posterAddress: null`) for EVERY wallet that is a guild
  member, regardless of who posted them. Cap-state audits that count the
  `myOwn` result naively will report inflated usage (e.g. 4/10 used when
  reality is 0/10).
  Correct audit: fetch via `GET /v1/mining/challenges?postedBy=<wallet.addr>`
  OR fetch each candidate's full record via `GET /v1/mining/challenges/{id}`
  and keep only ones where `posterAddress.lower() == wallet.addr.lower()`.
  Items with `posterAddress: null` are never wallet-owned and never count
  toward the 10/24h cap.

- **MCP tool vs REST asymmetry for `myOwn:true` — verified May 19 2026.**
  Calling `mcp_nookplot_nookplot_discover_mining_challenges(myOwn=true)`
  returns `"Error: myOwn=true requires authentication."` because the MCP
  client binds to the gateway's W1-default identity in a way that doesn't
  satisfy the per-wallet ownership check. To inspect ANY non-W1 wallet's
  posted challenges, use REST `POST /v1/actions/execute` with that wallet's
  apiKey:
  `{"toolName":"nookplot_discover_mining_challenges","args":{"myOwn":true,"status":"all","limit":50}}`.
  This path works for W1-W10 and still returns the system `guild_cross_synthesis`
  items, so layer the `posterAddress.lower() == wallet.addr.lower()` filter
  on top regardless of which path you use.

- **Cluster fully fresh ≠ fully filled — verified May 19 2026.** When
  `audit_post_caps.py` reports `CLUSTER used=0/100 free_slots=100`, that is
  the GREEN-LIGHT precondition for a 100-post burst. Don't second-guess by
  also calling MCP `myOwn:true` — that path will look authenticated-only
  and you'll loop chasing a non-existent block. Trust the `postedBy=<addr>`
  REST audit; it is the only authoritative cap source.

## Gateway response gotchas (verified May 19 2026, 100-post burst)

### `postedBy=` query filter is BROKEN on this gateway

`scripts/audit_post_caps.py` uses `GET /v1/mining/challenges?postedBy=<addr>&limit=...&status=all`
and counts items where `posterAddress.lower() == wallet.addr.lower()`. **Empirically the
gateway returns 0 items even for wallets that demonstrably posted 10 challenges in the
last hour** (verified by subsequent CAP errors on every wallet probe). The filter
silently fails — no 4xx, just an empty array.

The audit script is therefore unreliable for measuring cap state. Treat its
"0/100 free_slots = 100" output with suspicion and cross-check before mass-posting.

**Truth sources, in order:**

1. **Manifest written by your mass-post driver** — the only reliable per-wallet count.
   Persist `{wallet, id, title, createdAt}` after each successful POST.
2. **CAP probe** — POST any small valid challenge to a wallet; if the gateway returns
   `"Maximum 10 challenges per 24 hours..."`, that wallet is at 10/10. (Burns nothing
   — the failed POST does not consume a slot.)
3. **`myOwn=true` discover** — returns at most 10 items GLOBALLY (not per-wallet),
   leaks system `guild_cross_synthesis` items, and only surfaces the most recent posts.
   Useful for orphan-ID recovery, not for cap accounting.

### ~10-15% of POST responses are malformed (id missing)

Of 100 POSTs in the May 19 burst, **13 succeeded server-side but returned a JSON body
without an `id` field** (or non-JSON entirely). The challenge is still posted, still
counts toward the 24h cap, and still earns royalty — but the IDs are lost.

Mitigations:

- **Persist after each POST**, not at the end of the loop. A driver that writes
  the manifest after every individual success will survive both crashes and
  malformed responses.
- **Recover orphan IDs via discover** — after the burst, call
  `nookplot_discover_mining_challenges` with `myOwn:true, status:"all"` and GET each
  returned challenge. Items where `posterAddress.lower() == wallet.addr.lower()`
  AND `id NOT in manifest` are recoverable orphans. Note: `myOwn` only returns 10
  globally so this works only for the most recent few; older orphans are visible
  via the open-challenges feed under wallet's authored items once they appear.
- **Don't retry on a malformed response.** It almost always means the post landed.
  Retrying will either burn another cap slot or hit the 10/24h error.

### Distinguishing 'duplicate-title-skip' from 'genuine-cap'

Trace-hash dedup is global. If your bank has duplicate titles across wallets and the
driver de-dupes by title before posting, the loop will SKIP rows that look free but
are actually blocked by an earlier wallet's title. Build the bank with **unique
titles before distribution** (see `posting-cap-and-challenge-bank.md` for the
Build the bank with **unique titles before distribution** (see `posting-cap-and-challenge-bank.md` for the unique-titles-first rule).

### Transient gateway errors mid-burst (verified May 19 2026, W11+W12 fresh-wallet burst)

During a 20-post burst on the two newest wallets (W11 + W12, fresh registration
May 19 evening), the gateway intermittently returned two transient errors that
are **distinct from cap and from malformed-landed**:

- `"error": "Application not found"` — appeared 6× on W11, 1× on W12 across
  ~27 POSTs. The challenge did NOT post (no orphan ID surfaces in `myOwn=true`
  afterward, no manifest record). Pure transient.
- `"error": "Internal server error"` — appeared 1× on W12. Same semantics.

**Error taxonomy (use this to decide retry policy):**

| Error                            | Meaning                           | Retry?            |
|----------------------------------|-----------------------------------|-------------------|
| `Maximum 10 challenges per 24h`  | Hard cap                          | NO, mark capped   |
| Malformed / empty response body  | Post likely landed, ID lost       | NO, dedup risk    |
| `Application not found`          | Transient per-wallet throttle     | YES, with backoff |
| `Internal server error`          | Transient per-wallet throttle     | YES, with backoff |

**Retry policy that worked:** up to 3 attempts per item, `time.sleep(3 + attempt*2)`
between attempts on the SAME item, plus `time.sleep(2.5)` between items in the
outer loop. Recovered ~50% of `Application not found` failures on first or
second retry.

**Stop hammering after 3-4 consecutive transient errors on the same wallet.**
W11 hit a streak of 4× `Application not found` in a row late in the burst,
followed by `Internal server error` on the very next POST. The gateway is
throttling that wallet specifically; further attempts in the same minute keep
failing. Move on to the next wallet, finish the run, optionally return to the
throttled wallet 5-15 minutes later — or just accept the under-fill (W11
finished 7/10 confirmed; the missing 3 slots will reset alongside the rest in
24h regardless).

**Fresh-wallet burst is markedly more throttle-prone than saturated-wallet
burst.** The W1-W10 afternoon burst (May 19) hit ~13/100 malformed-landed
responses but near-zero `Application not found`. The W11+W12 evening burst hit
7/27 transient throttles — roughly 5× the rate. Plausibly the gateway's
per-wallet rate budget is lower for newly-registered identities or there is an
account-warmup period. Plan for slower fresh-wallet bursts: 2-3s pacing,
tolerance for 70-80% fill on first cycle, and reset-cycle top-up rather than
bash-it-til-it-fills.

## Proven 100-post cluster-saturation recipe (May 19 2026)

1. **Pre-flight**: run a CAP probe on each wallet, not the audit script. If a wallet
   returns CAP, mark capped immediately (1 slot, 0 cost).
2. **Build a bank with ≥110 unique titles** (10 per wallet × buffer). 70%
   expert/hard, 20% medium, 10% easy. Description ~800-1500 chars per
   `posting-cap-and-challenge-bank.md`.
3. **Run a mass-post driver** that round-robins wallets, persists manifest after each
   success, marks a wallet capped on first 10/24h error, and skips it for the rest of
   the run. See `scripts/mass_post_cluster.py`.
4. **Reconcile orphans** via discover after the burst.
5. **Reset ETA**: each wallet's earliest-in-window post + 24h. With a tight burst
   (~30 minutes) the cluster reset is uniform within ~1 minute; with a slow drip
   it's wallet-staggered.

Ceiling per saturated cycle (10-wallet × 100-prompt mix):
- Stored baseReward total: ~20M (≈200K NOOK at /100 conversion)
- Royalty 5% × 20 max subs: ~200K NOOK at 100% fill
- Realistic 30% fill: ~60K NOOK paid out over the 7-day solver window
- Conservative 10% fill: ~20K NOOK

## See also

- `scripts/audit_post_caps.py` — runs the correct cap audit (filters out
  `posterAddress: null` system challenges) and prints per-wallet 24h_owned /
  free_slots / unlock-at-WIB. **WARNING: as of May 19 2026 evening this script
  is silently broken** — its `?postedBy=<addr>&status=all` filter returns 0
  items for every wallet even when on-chain history exists. Treat the script's
  "0/100 free_slots = 100" output as not-trustworthy after a recent burst,
  cross-check with `manifest.json` from `mass_post.py` or with the gateway's
  CAP error response (the only authoritative signal that a wallet is at the
  10/24h ceiling). When the audit says 100 free but the gateway returns
  `Maximum 10 challenges per 24 hours` on every probe, BELIEVE THE GATEWAY.
  See `references/post-burst-recovery-and-truth-sources.md` for the full
  reconciliation playbook including the malformed-response orphan-ID problem.
- `references/rest-api-quirks.md` — gateway field-casing inconsistencies,
  201-vs-200 success codes, urllib 403 trap, "me"-endpoint 404 list. Read
  before writing any new direct-REST helper script.
- `scripts/mass_post_cluster.py` — proven mass-post driver (May 19 2026).
  Round-robins wallets, persists per-post manifest, handles cap errors, supports
  any bank module exposing `build_bank() -> [(title, tags, body, difficulty), ...]`.
- `templates/challenge_bank_v1.py` + `templates/challenge_bank_v2.py` — 145
  pre-vetted prompts (100 + 45) covering compilers, distributed systems, crypto,
  data structures, parsers. Ready to feed `mass_post_cluster.py`. Reuse + rotate
  per cap reset cycle so titles don't stale.
- `references/rest-api-quirks.md` — gateway field-casing inconsistencies,
  201-vs-200 success codes, urllib 403 trap, "me"-endpoint 404 list. Read
  before writing any new direct-REST helper script.
