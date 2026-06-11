# Verify queue discovery — REST returns markdown only (focus-wallet impact)

Confirmed May 22 2026 during a "fokus wallet 9" deep-dive audit on gateway 0.5.32.

## Concrete behaviour

`discover_verifiable_submissions` invoked via REST `POST /v1/actions/execute` returns
`result` as a **markdown-formatted string** (~4 KB cap), NOT a structured list:

- Solver address abbreviated to `0xprefix…suffix` (4 hex prefix + 4 hex suffix).
- Submission UUID is **not** included in the markdown table.
- Challenge title truncated to ~50 chars.
- Tried args `{format:'json'}`, `{raw:true}`, `{asJson:true}` — all still return markdown.
- Hard 4096-char cap on the markdown payload itself.

Direct REST submission-listing endpoints (also tried, all 404 on gateway 0.5.32):

- `GET /v1/mining/agents/{addr}/submissions`
- `GET /v1/agents/{addr}/submissions`
- `GET /v1/mining/submissions?address={addr}`
- `GET /v1/mining/verify/queue`

Returns `{"error": "Not found", "message": "Endpoint does not exist..."}`.

## Implication for "fokus wallet [N]" sessions

Cluster sock-puppet filtering by full solver address requires either:

1. **MCP** `nookplot_discover_verifiable_submissions` returns the structured list with full
   `solverAddress` + `submissionId` — but MCP is W1-bound, and using W1 to read other wallets'
   queues during a focus-wallet session crosses the "no other wallet touches" line. Surface this
   to the user before invoking, do not assume.
2. **Prefix/suffix match** against the cluster\_addrs map (lower-cased). The 4+4 hex collision
   space is ~10^10 → collisions are negligible at 15-wallet scale, so this is the practical workaround.
3. **Submission ID is still hidden.** Even with a matched row you cannot pay the comprehension /
   verify cost without the UUID. So the workaround is for *filtering* (rejecting cluster rows
   before paying anything), not for *executing* verifies.

## Recommended focus-wallet verify workflow

```
1. Probe my_guild_status with each cluster wallet's apiKey → build full cluster_addrs set
   (use the per-wallet apiKey, NOT W1 / MCP, to keep cluster-isolation clean)
2. Pull verify queue via REST (markdown), parse the table
3. For each row, take the 4+4 abbreviated solver and prefix/suffix-match against cluster_addrs
4. Mark rows where match=cluster as BLOCKED (sock-puppet rule); rest are "eligible-in-principle"
5. To actually verify an eligible row you need its submissionId — currently only MCP exposes it.
   During "fokus wallet [N]" raise this to the user as a hard constraint: external verifying is
   not reachable for focused-wallet sessions until either (a) the gateway adds full IDs to the
   REST response, or (b) the user explicitly authorises MCP-via-W1 read-only queue-reads.
```

## Rate limiter notes (same-session empirics, May 22 2026)

`/v1/actions/execute` enforces aggressive per-key rate limiting:

- A 4-call burst within ~10 s triggered `"Too many requests"` for 30-60 s.
- Recommended pacing: **≥8 s between sustained calls**, **30-90 s after a 429**.
- The cluster-guild-probe loop (15 wallets × `my_guild_status`) at 2.5 s spacing completed
  cleanly without any 429 — different keys are rate-limited independently, so per-wallet
  loops are cheap; what gets throttled is repeated calls on the **same** apiKey.

## Cluster guild map (for prefix-matching reference, May 22 2026)

```
W1  hermes      0x5fcF1aE1  → 100017 The Lyceum Collective
W2  9dragon     0x5b82be85  → 9      Social Contract
W3  kevinft     0xDf5bc41E  → 100002 SatsAgent Mining Collective
W4  aboylabs    0xdbAFE90B  → 100017 The Lyceum Collective
W5  reborn      0xd01767C9  → 100032 Quill Edge Research Lab
W6  satoshi     0xdE44c354  → 100045 Jetpack
W7  badboys     0xa987Be54  → 100045 Jetpack
W8  rebirth     0xFb671453  → 100045 Jetpack
W9  john        0x8B0b4D69  → 100045 Jetpack    (tier3 1.9x, 0 stake)
W10 joni        0x5A1876a5  → 100000 Knowledge Collective
W11 WhiteAgent  0xcdDb0f53  → 10     nookplot avengers
W12 PanuMan     0xC339a172  → 10     nookplot avengers
W13 hemi        0x073e127e  → 100002 SatsAgent Mining Collective
W14 kicau       0x13490D89  → 100046 The Commission
W15 lucky       0x8863b1F7  → 100002 SatsAgent Mining Collective
```

Use this snapshot for fast manual cluster-row rejection on a verify queue dump. Refresh by
re-probing `my_guild_status` per wallet whenever guild membership changes.
