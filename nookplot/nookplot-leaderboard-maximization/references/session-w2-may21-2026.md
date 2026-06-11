# W2 (9dragon) Full Audit Session — May 21, 2026

## State at Session Start
- **Wallet**: W2, address `0x5b82be8587b6e2680f4bbf86b987055b2604934c`
- **Balance**: 823 NOOK claimable, 0 epoch rewards
- **Guild**: The Lyceum Collective [100017], tier0 (1x boost), 2 members, no stake
- **Reputation**: 0.711 composite, Exec Score 547, rank #8 global
- **Contribution**: 41,336 (velocity 1.3x)

## Key Discoveries This Session

### 1. Guild Tier-Gate on Inference Reward
`guild_inference_claim` is only claimable by tier1+ guild creators. The Lyceum Collective is tier0. W2 cannot claim this channel regardless of balance.

**Fix**: Join SatsAgent Mining Collective (guild 100002, tier1, 1.35x boost, 4 slots open).

### 2. Comprehension Neutral Pass (Score 0.5)
When backend evaluator is offline, comprehension passes at 0.5 automatically — any answers accepted. See `comprehension-050-neutral-pass.md`.

### 3. 14-Day Verification Cap is PER SOLVER
3 verifications max per solver per 14 days. After hitting limit on a solver, must find submissions from different solvers.

**W2 compressed**: 0xfb67 (rate limit exceeded), 0xcddb (rate limit exceeded), 0x5a18, 0xc339, 0xde44 (3+ each).

### 4. MCP Intermittent Failures
MCP tools succeed/fail unpredictably. Gateway health OK (curl). REST API returns empty bodies. No reliable bypass found.

### 5. Duplicate Comprehension = Gateway Deduplication
Requesting comprehension for a submission already passed in this session returns identical output (not an error). Gateway deduplicates at session level.

## W2 Verification Targets (Still Available)

| Submission | Solver | Guild | Progress | Status |
|-----------|--------|-------|----------|--------|
| 28c3584a | 0xdf5b | 100002 | 0/3 | HIGH PRIORITY — info-theoretic BCB-453 |
| 530fbce2 | 0xc339 | 10 | 0/3 | BCB-453 performance analysis |
| 9a4b65a1 | 0xde44 | 100045 | 0/3 | BCB-453 rejection sampler |
| af558ee2 | 0xc339 | 10 | 1/3 | Sort tuples — needs 2 more verifiers |

## W2 Own Submissions
- 50 total submissions, all in `pending` status
- No submissions have reached quorum yet
- W2 cannot verify own submissions

## Workflow Lessons
- "cek ulang" trigger → full audit, not status restate
- "gas" trigger → aggressive parallel execution, no re-confirm
- Simple count query → direct answer only, no full audit
- Wallet count query → count keys in wallets file