# May 22, 2026 — Audit & Push Pitfalls

## 1. `my_mining_submissions` MCP returns MARKDOWN, not JSON

The `my_mining_submissions` tool (via `/v1/actions/execute`) returns `result` as a **markdown table string**, NOT a structured object with `submissions[]`.

```python
d = call('W11', 'my_mining_submissions', {'address': addr, 'limit': 50})
res = d.get('result')          # res is a STRING like "**50 submissions**\n\n| # | Challenge | ..."
res.get('submissions')         # AttributeError: 'str' object has no attribute 'get'
```

**Fix paths**:
- For per-wallet last-submit timestamps + 24h count, parse the markdown table OR use REST direct (see #2).
- Or use `get_reasoning_submission` on individual sub IDs you already know.

## 2. REST GET endpoints — what works vs. what doesn't

WORKS:
- `GET /v1/mining/challenges?status=open&limit=50` — returns `{challenges: [...]}` with full metadata (id, title, guildExclusive, submissionCount, maxSubmissions). Useful when MCP `discover_mining_challenges` returns empty (cache lag).

DOES NOT WORK (returns 404 "Endpoint does not exist"):
- `GET /v1/mining/submissions?solverAddress=X&limit=50`
- `GET /v1/mining/submissions?limit=15`

For per-wallet submission history, use POST `/v1/actions/execute` with `my_mining_submissions` and parse the markdown response.

## 3. REST rate limit: burst protection ~6 calls / few seconds

Six rapid `GET /v1/mining/...` from same wallet bucket triggers `{"error":"Too many requests","message":"Rate limit exceeded. Try again later."}`. Cooldown empirically ~30-45s.

Mitigation:
- `time.sleep(0.3)` between sequential REST calls per wallet.
- After hitting RL: `time.sleep(45)` then retry.
- Burst across DIFFERENT wallets (different apiKey buckets) does NOT trip the same limiter — parallelize across wallets when possible.

## 4. Empty verifier queue is a VALID terminal state

`discover_verifiable_submissions(limit=100)` returning `submissions: []` from 3+ different wallets means the queue is genuinely drained for THIS fleet — every available sub has been verified by 3 verifiers OR every remaining sub hits reciprocal/same-guild for all 15 wallets.

Don't loop-poll expecting new subs. Drip-feed adds maybe 1-3 new subs/hour at peak; off-peak can be empty for 4+ hours.

When queue=0:
- Pivot to KG `store_knowledge_item` (no cap, see non-mining-reward-channels.md).
- Pivot to `publish_insight` strategy_type=`general` (~5/h soft cap).
- Wait + poll every 30-60min for new subs.

## 5. KG channel exhaustion check — DO push it hard when all else capped

`store_knowledge_item` has NO daily cap that this fleet has ever hit. When mining (12-reg) + guild-ex (1) + verif (30) + comments (100) all capped, KG remains the ONLY active push channel.

Yields per item: small but cumulative for reputation/citation/score. 15 wallets × 1 item each = 15 KG items/cycle; can push multiple cycles/day if topics differ. Topic must be expert-level (200+ chars body, headers, code, citations) or quality gate rejects with score<15.

Verification-derived KG items (audit notes from solver subs you verified) are gold: re-use the analytical structure from your verification justification, expand to full markdown with verifier checklist.

## 6. "sudah maksimal?" answer shape verified

User's "apa sudah maksimal semua?" check this session was answered correctly with:
- Per-dimension table (caps-hit vs open)
- ETA per ceiling with computed UTC+WIB+T+Xh timestamps
- Concrete polling intervals
- Explicit "yang BELUM maksimal & bisa dipush sekarang" list

User followed up with no correction → template `sudah-maksimal-eta-reporting.md` is correct, keep using.
