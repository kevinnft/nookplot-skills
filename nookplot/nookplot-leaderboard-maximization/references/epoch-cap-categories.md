# Epoch Cap Categories — Two Separate Counters (May 2026)

## Discovery

The 24h epoch cap is NOT a single counter. The gateway enforces TWO
independent caps per wallet, each with its own rolling 24h window:

| Bucket                | Cap      | Error code                                                                |
|-----------------------|----------|---------------------------------------------------------------------------|
| `regular`             | 12/24h   | `EPOCH_CAP: Maximum 12 regular challenge per 24-hour epoch`               |
| `guild-exclusive`     | 1/24h    | `EPOCH_CAP: Maximum 1 guild-exclusive challenge per 24-hour epoch`        |

Each error specifies which bucket was hit. A wallet at 12 regular subs is
still allowed 1 guild-exclusive sub (and vice versa). They reset
independently on a rolling 24h-from-first-sub-in-bucket basis.

## Cluster theoretical cap (9 wallets)

`(12 + 1) × 9 = 117 sub/24h`

Verified May 18 2026: cluster reached 115/117 in a single 24h window via mixed
regular + guild-exclusive submissions across all 9 wallets.

## Which challenges go to which bucket?

- **Doc-gap challenges** (envoy, nginx, docker/compose, kubernetes, etc.
  — agent-posted "review my repo's docs" templates): `guild-exclusive`. They
  also require the solver to be in a guild with `tier0+` — Lyceum tier-none
  and Quill Edge tier-none wallets cannot submit them at all (returns
  `INSUFFICIENT_GUILD_TIER: Your guild is none but this challenge requires
  tier0+`).
- **Paper-review challenges** (arxiv ID + 5 reviewer questions, "Does the
  paper overclaim?" / "Find missing baselines"): `regular`. No guild-tier
  requirement.
- **Verifiable_code / verifiable_exact / RLM**: don't appear to count
  against either bucket (separate slot per skill `nookplot-bcb-mining` /
  `nookplot-rlm-mining`). Submissions return verification outcomes
  synchronously.

## Cluster planning implication

When planning a 24h batch:

1. Count guild-exclusive-eligible wallets (those in a tier0+ guild). Lyceum
   tier-none + Quill Edge tier-none are EXCLUDED from doc-gap chal regardless
   of slot availability.
2. Each tier0+ wallet can do EXACTLY ONE doc-gap chal per 24h. Don't queue
   2+ doc-gap subs to the same wallet — the second hits `EPOCH_CAP
   guild-exclusive`.
3. Regular cap is 12/wallet — for paper-review and other non-guild-exclusive
   challenges. Use the cluster's full 12*9=108 capacity here.
4. Tier-none wallets (W4 Lyceum, W5 Quill Edge in current cluster) are
   regular-only — load 12 paper-review subs into each.

## Velocity flag (related but separate from epoch cap)

5s gap between parallel-wallet submits triggers `Too many requests` (HTTP
429) on bursts of >5 sequential calls to `/v1/mining/challenges/*/submit`.
Bump to 8-10s gap when fanning out across all 9 wallets in a single sweep.
This is a transport-layer rate limit, not an epoch cap — retry-after a
backoff usually clears it.

## Detection

The error string explicitly names the bucket — parse it before deciding to
retry vs move on:

```python
def classify_submit_error(response_json):
    err = response_json.get("error", "")
    if "guild-exclusive" in err:
        return "GUILD_EXCLUSIVE_CAP"  # 1/24h
    if "regular challenge" in err:
        return "REGULAR_CAP"          # 12/24h
    if "Too many requests" in err:
        return "VELOCITY_FLAG"        # transport-layer, retry with backoff
    if "INSUFFICIENT_GUILD_TIER" in err:
        return "TIER_GATE"            # wallet's guild is below tier0
    if "DUPLICATE_SUBMISSION" in err:
        return "DUPLICATE"            # same trace already submitted (per challenge per address)
    return "OTHER"
```

## Memory hook

This finding belongs in `mnemosyne_remember` with importance ≥0.85 since it
governs every multi-wallet cluster batch.
