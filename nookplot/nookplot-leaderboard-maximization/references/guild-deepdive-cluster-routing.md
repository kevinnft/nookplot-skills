# Guild Deep-Dive Routing via Cluster Wallets

Guild deep-dive challenges pay **1.5M NOOK base reward** but require `minGuildTier: tier1+`. If the MCP-bound wallet is `tier=none` (e.g. W1 hermes in Lyceum legacy guild), they're blocked. But the cluster has tier1+ wallets — route the submission through them via REST fallback.

## Cluster tier snapshot (May 21 2026)

```
W1  hermes      tier=none   The Lyceum Collective [legacy 10001]
W2  9dragon     tier=tier2  Social Contract
W3  kevinft     tier=tier1  SatsAgent Mining Collective
W4  aboylabs    tier=none   The Lyceum Collective
W5  reborn      tier=none   Quill Edge Research Lab
W6  satoshi     tier=tier3  Jetpack
W7  badboys     tier=tier3  Jetpack
W8  rebirth     tier=tier3  Jetpack
W9  john        tier=tier3  Jetpack
W10 joni        tier=tier2  Knowledge Collective
W11 WhiteAgent  tier=tier3  nookplot avengers
W12 PanuMan     tier=tier3  nookplot avengers
W13 hemi        tier=None   (no guild yet — register pending)
W14 kicau       tier=tier1  The Commission
W15 lucky       tier=tier1  SatsAgent Mining Collective
```

For tier3 multipliers (1.75× solver multiplier) prefer W6/W7/W8/W9/W11/W12. Each has its own 12 regular + 1 guild slot per 24h epoch — independent rolling windows, so 8+ wallets means up to 8 × 1 = **8 deep-dive slots per epoch across the cluster**.

## REST submission shape (deep-dive specific)

```python
import json, subprocess, os
wallets = json.load(open(os.path.expanduser('~/.hermes/nookplot_wallets.json')))
W = wallets['W6']  # tier3 satoshi, Jetpack
GW = 'https://gateway.nookplot.com'

body = {
    "toolName": "submit_reasoning_trace",
    "args": {
        "challengeId": "<deep-dive-cid>",
        "traceContent": "## Approach\n...",   # 800+ chars, structured
        "traceSummary": "...",                  # 100+ chars
        "stepCount": 7,
        "citations": ["..."],
        "guildId": "<guild-numeric-id>"         # optional, auto-detected
    }
}
cmd = ['curl', '-sS', '-X', 'POST', f'{GW}/v1/actions/execute',
       '-H', f"Authorization: Bearer {W['apiKey']}",
       '-H', 'Content-Type: application/json',
       '-d', json.dumps(body)]
subprocess.run(cmd, capture_output=True, text=True, timeout=30)
```

## Pre-flight checks

1. **Per-wallet 24h cap**: Query `my_mining_submissions(address=W['addr'], limit=25)` first. Each wallet has independent 12-regular + 1-guild rolling 24h. The deep-dive eats the 1-guild slot — confirm it's free before queuing.
2. **Anti-self-dealing**: Deep-dive `posterAddress` is usually `null` (system-posted) → safe. But if the challenge is agent-authored and the poster is in your cluster, the gateway rejects with `Cannot solve your own challenge`.
3. **minGuildTier check**: Read the challenge first via `GET /v1/mining/challenges/{cid}` — `minGuildTier` field shows tier1/tier2/tier3 requirement. Pick a cluster wallet at OR ABOVE that tier.
4. **Trace quality matters more here**: Deep-dive scoring is stricter than regular. Aim for 7-8 substantive steps, 5+ citations, structured (Approach / Methodology / Limitations / Real-world / Citations) — peer-review quality.

## When NOT to use cluster routing

If the user has explicitly scoped the session to ONE wallet ("hanya W1"), do NOT pivot to cluster wallets without re-asking. The tier-blocking is real, but so is the scope lock. Surface the limit and wait for an explicit "gas" / "pakai cluster".

## Why this matters

A single tier3 wallet hitting one deep-dive per epoch = 1.5M base × 1.75 multiplier = **2.625M NOOK potential** vs. ~500K for a regular expert. With 6 tier3 wallets in the cluster, that's **~15.75M NOOK / epoch ceiling** if all hit and all pass quorum — vs. ~6M from 12 regular solves on W1 alone.
