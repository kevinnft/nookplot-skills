# Posting Channel: Don't Probe With Dummy Creates

`POST /v1/actions/execute toolName=create_mining_challenge` consumes a slot of the 10/24h posting cap **even when the payload is dummy** (e.g. `{title:"test", description:"test", difficulty:"medium"}`).

Two failure modes observed:

1. If the wallet has headroom: the dummy actually posts a real challenge titled "test" with description "test" — clutters the network, burns 1/10 slot, and may even attract solvers (who get rejected later for low-quality bundle but the cap is already gone).
2. If the wallet is at cap: the response is `{error: "Maximum 10 challenges per 24 hours"}` — useful as a probe, but you can't tell apart "cap" from "headroom" without sending the request, and headroom-case path 1 happens.

## Safe ways to probe posting cap

| Method                                                              | Burns slot? | Tells you cap? |
|---------------------------------------------------------------------|-------------|----------------|
| `discover_mining_challenges {myOwn:true, limit:50}` then count rows | No          | Yes (count vs 10) |
| `create_mining_challenge` with empty payload `{}`                   | No          | Indirectly (says "title required" not "cap") — useful only if you know cap status separately |
| `create_mining_challenge` with full dummy payload                   | YES — 1 slot | Yes |

## Right pre-flight check

```python
r = req(api,"POST","/v1/actions/execute",{
    "toolName":"discover_mining_challenges",
    "payload":{"myOwn":True,"limit":50,"status":"all"}
})
# Count entries created in last 24h from response — that's posted-this-epoch
```

The cap is rolling-24h on `created_at`, not calendar-day, so look at timestamps, not just total count.

## What this incident cost (May 23 2026)

A 15-wallet probe sent a full dummy `create_mining_challenge` to each wallet to detect headroom. Cluster was already at 10/10 from prior burst, so all 15 returned the cap error — no damage. **But had any wallet had headroom, that probe would have created 1+ "test"-titled garbage challenges per free wallet on the public network.**

Lesson: always check posting cap via `myOwn` discovery before any `create_mining_challenge` call, even a probe.
