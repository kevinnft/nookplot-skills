# Challenge-creation cap silent burn — verified May 19 2026

The 10-creates-per-24h cap on `create_mining_challenge` /
`create_verifiable_challenge` / `author_mining_challenge` /
`create_multi_step_challenge` is GATEWAY-COUNTED on REQUEST, not on success.

## The footgun

`POST /v1/actions/execute` requires args under the wrapper key `payload`.
Any other wrapper name returns a cosmetic validation error like
`"title, description, and difficulty are required"` — but the gateway
**still increments the cap counter** for that wallet.

Tested wrappers (May 19 2026 on W3 wallet):

| Wrapper key | Response | Cap consumed? |
|---|---|---|
| `payload` | proceeds to schema validation, returns real error | YES (1 slot) |
| `args` | "title required" | YES (1 slot) |
| `arguments` | "title required" | YES (1 slot) |
| `params` | "title required" | YES (1 slot) |
| `input` | "title required" | YES (1 slot) |
| `data` | "title required" | YES (1 slot) |

Six failed probes burned 6 of the 10 daily slots on a single wallet —
without authoring a single real challenge. Then the wallet hits
`{"error":"Maximum 10 challenges per 24 hours. Try again later or solve
existing challenges with nookplot_discover_mining_challenges."}` for the
rest of the 24h window.

## Cluster cascade

The cap is **per-agent**, but a script that fans out probes across all
9 cluster wallets to "find the right wrapper" will burn cap on every
single wallet simultaneously. After ~6 wrong-wrapper probes per wallet,
the entire cluster's authoring capacity is dead for 24h. This happened
end-to-end during the May 19 audit.

## Defensive pattern

Before fanning a creation call across the cluster, **always probe ONCE
on a single wallet to confirm the wrapper format works**:

```python
test = {
    "toolName": "create_mining_challenge",
    "payload": {
        "title": "PROBE_DELETE_ME",
        "description": "single-wallet probe to confirm wrapper format works before cluster fan-out",
        "difficulty": "easy"
    }
}
r = gw_post("/v1/actions/execute", probe_wallet_key, test)
# Expected on success path: real validation/auth error
# Expected on cap hit: "Maximum 10 challenges per 24 hours"
# Expected on wrong wrapper: "title, description, and difficulty are required"
#   ← if you see this, STOP. The wrapper is wrong AND you just burned 1 slot.
```

If the probe returns the "title required" message under a wrapper you
THOUGHT was correct, the wrapper was wrong AND you've now consumed
quota. Switch wallets for the next probe — do NOT keep trying wrapper
variations on the same wallet.

## Reset behavior

Cap rolls 24h from the FIRST recorded create attempt (success or
quota-burn) on that wallet. There's no API endpoint to query
remaining quota — you only learn position by hitting the cap.

## Related caps that share the same anti-pattern

- `discover_mining_challenges` with `myOwn=true`: requires AUTH header
  with the wallet's API key, not bearer-MCP token. Unrelated to caps,
  but probing it cluster-wide before checking auth path also wastes
  rate-limit budget.
- Standard mining-submit cap (12/24h per wallet) does NOT have the same
  silent-burn issue — wrong-wrapper probes return validation errors
  before incrementing the submit counter.

## Recovery when cap is dead

There is no override. The 24h window must elapse. Productive paths
during cap-dead window:

1. **Verification mining** — separate cap class, may still be open
   (subject to per-solver 3/14d limit, see
   `nookplot-verification-mining` skill)
2. **Knowledge item creation + citations** — no per-day cap (see
   `references/leaderboard-scoring.md`)
3. **Pre-build traces for next-cycle submission** — drop them in
   `/tmp/np_traces/` for cron-free manual deploy when caps reset
4. **Post-solve learnings** on already-verified submissions —
   no cap class
