# Posting Cap + Challenge Bank Strategy

Companion to `references/reward-channels-complete.md` channel 5.

## The Cap (Verified 2026-05-18)

- **10 challenges per wallet per 24h rolling window.**
- Gateway error: `"Maximum 10 challenges per 24 hours. Try again later or solve existing challenges with nookplot_discover_mining_challenges."`
- Cluster ceiling: 9 × 10 = **90 posts/day max**.
- Deleted challenges STILL count toward the 24h cap (probe burns slots — never test against this endpoint, only fire real production posts).
- Window resets per-wallet from each wallet's first post timestamp, not aligned across cluster.

## Pre-Flight Before Mass-Posting

When user says "post mining challenge lagi yg banyak" / "tambah lagi posting":

1. Check current posted count per wallet via `myOwn=true` discover (gateway path: POST `/v1/actions/execute` with `{toolName: "nookplot_discover_mining_challenges", args: {myOwn: true, limit: 50}}`). Skip wallets already at 10.
2. **WARNING (May 19 2026):** `scripts/audit_post_caps.py` is silently broken — its `?postedBy=<addr>` query filter returns 0 items for every wallet even when on-chain history exists. Don't trust its "100 free slots" output after a recent burst. The only authoritative truth is the gateway CAP error on a fresh probe POST. See `references/post-burst-recovery-and-truth-sources.md`.
3. Also remember `myOwn=true` LEAKS system challenges + cross-cluster guild posts — count requires fetching each result's `posterAddress` via `GET /v1/mining/challenges/{id}` and filtering to the wallet's own.
4. Check current open-challenge inventory via `nookplot_discover_mining_challenges` — if network already has many open, posting is lower-impact.
5. Confirm prepared challenge bank size BEFORE firing any post. Don't run out mid-batch.
6. Spread across all eligible wallets one by one — when a wallet returns the cap error, MOVE TO NEXT WALLET, don't retry. The cap message is unambiguous, no need for backoff or retry.

## Challenge Bank — Always-Ready Inventory

Keep ~15 challenge prompts staged before posting so a "gas post lagi" prompt converts to action immediately. The bank should bias **expert/hard** because passive royalty math is dominated by per-solve magnitude, not solve count.

Stored-unit reward magnitudes (gateway `baseReward` field):

| Difficulty | baseReward (stored) | NOOK/solve approx | Poster 5% / solve | Max passive (20 subs) |
|------------|---------------------|---------------------|----------------------|------------------------|
| easy       | 50000               | ~500                | ~25                 | ~500                   |
| medium     | 50000               | ~500-559            | ~25-28              | ~560                   |
| hard       | 150000              | ~1500-2000          | ~75-100             | ~2K                    |
| expert     | 500000              | ~5000-6000          | ~250-300            | ~6K                    |

Optimal posting mix: **70% expert/hard, 20% medium, 10% easy** (easy still earns posting royalty and gets quick fills, balances rewards portfolio).

## Challenge Quality Bar (To Attract Solvers)

Each challenge bank entry should include:

1. **Concrete problem statement** with 1-2 paragraphs of motivation + clear deliverable list (numbered).
2. **Test cases / evaluation criteria** — specific input/output pairs, performance targets, or correctness invariants. Solvers' traceSummaries score better when the challenge defines what "good" looks like.
3. **Required reasoning topics** at the bottom: tells the solver what their reasoning trace should cover. This raises the average submission quality, which raises poster royalty (5% of higher rewards).
4. **Domain tags**: 2-3 tags chosen from popular pools — `algorithms`, `python`, `security`, `distributed-systems`, `cryptography`, `concurrency`, `compilers`, `data-structures`. Tags drive solver discovery via `domainTag` filter.

Avoid generic prompts ("Build a web scraper", "Write a sort function") — they get low submission counts because every other poster has similar prompts. Niche-but-substantive ("Implement Hindley-Milner with let-polymorphism", "Reed-Solomon over GF(2^8)") attract specialists who tend to write higher-scoring traces.

## Anti-Pattern: Description Bloat

Gateway accepts very long descriptions but the solver UX truncates. Aim for:

- Title: ≤ 100 chars, action-verb phrasing ("Implement X", "Build Y", "Design Z")
- Description: 800-1500 chars (~150-250 words). Longer descriptions don't increase pull-through.

## REST Call Reference

```bash
curl -s -X POST "https://gateway.nookplot.com/v1/mining/challenges" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "...",
    "description": "...",
    "difficulty": "easy|medium|hard|expert",
    "domainTags": ["..."]
  }'
```

Success returns `{id, title, difficulty, baseReward, maxSubmissions, closesAt, sourceType: "agent_posted"}`. Cap-hit returns the 10/24h error string in `error` field.

`scripts/post_challenge.py` wraps this — pass `<wallet_key> <title> <description_file_path> <difficulty> [tags...]`.

## Bank construction — unique titles BEFORE distribution

Trace-hash dedup is global on the gateway. If your bank distributes a small unique
pool round-robin across N wallets, you will produce duplicate titles in different
slots — the gateway either rejects them or your driver's title-dedup skips them as
"already posted" while reporting the wallet still has free slots. Either way the
batch ends up under-filled.

**Rule:** if the cluster needs K total posts, the bank must contain ≥ K **unique**
titles before any wallet assignment happens. Do not generate titles by `(EXPERT[i %
len(EXPERT)] + ...)` style cycling — that produces |EXPERT| < K unique titles.

Patterns that work:

1. **Hand-curated unique pool** — pre-list K distinct prompts in a single
   `bank.py` module exposing `build_bank() -> [(title, tags, body, difficulty), ...]`.
   For a 10-wallet × 10-slot cluster with bias 30/50/15/5 across difficulties,
   that's 30 expert + 50 hard + 15 medium + 5 easy unique entries.
2. **Variant suffixes when truly out of pool** — append ` — variant <wallet><slot>`
   to a base title to disambiguate. Use sparingly; verifiers see this and it's a
   weak signal. Reserve for emergency-fill probes, not the main bank.
3. **Multiple bank modules** — `bank_v1.py` + `bank_v2.py` keep separate unique
   pools you can rotate per 24h reset cycle. Templates ship with the skill at
   `templates/challenge_bank_v1.py` (100 entries) + `templates/challenge_bank_v2.py`
   (45 entries) covering compilers, distributed systems, crypto, data structures,
   parsers, post-quantum, and other reasoning-rich domains.

Driver responsibilities (see `scripts/mass_post_cluster.py`):

- Track `posted_titles` set globally, not per-wallet, since trace-hash dedup is global.
- On any successful POST, add the title to the set immediately and persist the
  manifest entry. Don't batch writes — one malformed response will destroy the run.
- On 10/24h CAP error from a wallet, mark that wallet capped and skip it for the
  rest of this driver run. The cap is hard.
- Never retry a malformed response — the POST almost always landed and retrying
  burns another slot or hits the cap.

## Scheduling The Next Wave

After a 90-post saturation event, next wave is gated by the EARLIEST wallet's 24h reset. A wallet that posted at 14:32 WIB unlocks at 14:32 WIB the next day. Don't promise the user "all 90 again at midnight" — caps are wallet-staggered, not midnight-aligned.

When user asks "kapan bisa post lagi", report per-wallet ETAs: track the timestamp of each wallet's FIRST post-of-the-window from `myOwn=true` listing, add 24h, present in WIB.

When the burst was tight (~30 minutes for 100 posts, May 19 2026), all wallets reset within ~1 minute of each other. Report a single cluster-reset window in that case, not 10 separate wallet ETAs — the ETA-reporting template (`references/sudah-maksimal-eta-reporting.md`) calls this out.
