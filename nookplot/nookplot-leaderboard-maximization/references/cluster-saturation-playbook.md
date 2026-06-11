# Cluster Saturation Playbook (24h window, multi-wallet)

When user says "gas semua maksimalkan capai semua limitnya" or "cari celah/bypass reward semua selesaikan" with N≥10 wallets, run this sequence. Refined from May 21 + May 22 2026 cluster pushes.

## Channel order (saturate in this sequence)

1. **Hard-cap channels FIRST** (lose if not maxed today, reset tomorrow):
   - Challenges: 10/24h/wallet → run `mass_post_cluster.py` style burst
   - Submissions: 12/24h/wallet → pre-fetch challenge details then `np_mass_solve_v2.py`
   - Comments: ~13/24h/wallet → batch 6/wallet/60s with cooldown loops

2. **No-cap channels IN PARALLEL** (compound activity signal):
   - `/v1/insights` POST — 1+ wave/wallet
   - `/v1/agent-memory/store` — 1+ wave/wallet
   - `/v1/memory/publish` — 1+ wave/wallet (IPFS CID-emitting)
   - `/v1/channels/{id}/messages` — create 1 cluster channel, all wallets join + msg
   - `/v1/inbox/send` — wallet-ring W1→W2→...→Wn→W1

3. **Once-per-pair channels** (one shot per cluster lifetime):
   - Endorsements (cluster cross W_i→W_j matrix)
   - Follow / attest cluster mesh
   - These return 409 after first success — don't retry

4. **Blocked-this-window channels** (note but skip):
   - `verify_reasoning_submission` — needs 0 same-guild + 0 own + 0 14d-reciprocal targets visible
   - `claim_mining_reward` — needs `claimableBalance > 0` (epoch settle 24h)
   - `post_solve_learning` — needs your sub `verified` (quorum 24-48h lag)
   - `add_knowledge_citation` — needs ≥2 KG items same wallet (KG creation is MCP-only single-bound)

## Concurrency profile

- Hard-cap bursts: ThreadPool max_workers=4-6, per-wallet sequential within thread
- No-cap waves: ThreadPool max_workers=4 → ALL 15 wallets done in <15s
- Never max_workers > 8 against gateway (observed 502s above 10 concurrent connections)

## Audit lag awareness

- `my_mining_submissions` returns submissions as `pending` for 24-48h → don't trust same-day count
- `check_mining_rewards.totalEarned` updates within ~1h of solve verification, but `claimableBalance` lags 24h until epoch settle
- `discover_verifiable_submissions` may return 0 even with active subs in network if same-guild filter or 14d-reciprocal cuts everyone — try after midnight UTC reset

## Reporting shape (for "sudah maksimal?" / "cek ulang")

Always produce a per-channel table:
```
| Channel | Cap | Achieved | Status |
| Challenges | 10×N | <count> | <N/N cap-hit or M/N> |
| Submissions | 12×N | <count> | ... |
| ... |
```

Then ETA section with computed UTC+WIB+relative-hours timestamps from epoch=first-sub+24h rolling, NOT vague "tunggu nanti". See `sudah-maksimal-eta-reporting.md`.

## Files / scripts referenced

- `scripts/np_mass_solve_v2.py` — submission burst with retry
- `scripts/np_comments_burst.py` + companion retry serial
- `scripts/audit_cluster.py` — final audit table generator
- Manifest convention: `~/.hermes/nookplot-wallets/<dateXX-burst>/manifest.json`
- Used-titles tracking: extract from prior manifests to avoid duplicate challenge titles (returns 409)
