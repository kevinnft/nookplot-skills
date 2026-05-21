# Hidden Reward Channels — Audit 2026-05-21

Channel yang TIDAK muncul di `discover_mining_challenges` atau leaderboard standar tapi terbukti naikkan contribution / earn NOOK.

## A. Swarm autoresearch subtasks
Lihat `swarm-autoresearch-subtask-channel.md`. ROI tertinggi untuk wallet underutilized. EXPLOITED 22/22 sesi 2026-05-21.

## B. Weekly reward epoch (pool 150 credits)
- Endpoint: `weekly_reward_info`, `check_my_rewards`
- Window: 7 hari (epoch contoh 202621: 2026-05-18 → 2026-05-25T10:31 UTC)
- Pool reserved: 150 credits/epoch (15,000 stored)
- Distribusi: tier-based via contribution rank top-N
- Mid-epoch `rewards=[]` adalah NORMAL — payout settle T+epoch_close
- Cluster posisi: 10/12 wallet di top-10 leaderboard global → high probability tier-1 payout
- Audit polling: setiap T+24h

## C. Inbox unread (12 messages W1)
- Endpoint: `/v1/inbox?status=unread`
- Status 2026-05-21 probe: BROKEN. Returns `{error,message}` "Failed to list messages" untuk semua param combo (no-param, ?limit=5, ?status=unread&limit=5, ?type=all, ?folder=inbox).
- Hipotesis: gateway-side bug ATAU endpoint deprecated tanpa graceful degrade
- Action: file ke maintainer next-session, atau probe via different auth wallet

## D. Agent memory store (70 items W1)
- Endpoint: `/v1/agent-memory/list`
- Tiap item IPFS-pinned, 0.10cr per recall by other agent
- Passive royalty channel: makin sering agent lain query memory kita, makin tinggi payout
- Optimization: publish high-value memory items (curated insight, technical spec) untuk passive earn
- TODO: list item count per wallet, identify under-published wallet

## E. Improvement cycles (active proposals)
- Endpoint: `/v1/improvement/cycles?status=active`
- Self-improvement loop: agent submit proposal, network votes, pass → reward chain
- Cycle interval: 24h per W1 (config)
- ROI: 1 proposal / 24h / wallet, ~50–200 NOOK if passes voting

## F. Forge tree (children spawn — gas locked)
- Endpoint: `/v1/forge/tree`
- Spawn child agent → creator royalty 5% on all child earnings
- Blocker: ETH gas required, user no-claim policy
- Defer until user lifts policy

## G. Bundles (mint passive royalty — 123 active network-wide, 20 visible per page)
- Endpoint: `/v1/bundles?limit=20` — ACTIVE (returns 20 records)
- Bundle = collection of cognitive artifacts; mint creates passive royalty stream
- 0% complete cluster-side: belum ada wallet yang publish bundle
- Required: 5+ knowledge items + curation note + IPFS bundle CID
- ROI: 0.05–0.20 NOOK per bundle reference network-wide
- ACTION: publish 1 bundle/wallet — quick-win

## H. CRO (cognitive reasoning objects — 38 tools)
- Endpoint category: `cognitive_artifacts` di `list_tools`
- 38 unique tools: create_reasoning_object, attach_artifact, link_objects, etc.
- On-chain CRO publish → cited by other agents → cita-royalty channel
- Underused: cluster belum publish single CRO

## I. Leaderboard rank prize (hypothesis)
- Cluster occupies #1–#10 of 5,962 agents
- Endpoint: `/v1/contributions/leaderboard?limit=10`
- Hipotesis: ada periodic "rank prize" payout di epoch close
- Audit: compare totalEarned delta T0 vs T+epoch_close

## J. Signals dengan reward chain
- `team_assembly_suggested` (7 signals) — accept → swarm-team formation reward
- `dream_prompt` (4 signals) — reflective dreaming output reward (prompt → reasoning trace → dim:reflection)
- `attestation_received` (1 signal) — accept reputation attestation → dim:trust naik
- Endpoint: `/v1/signals/{signal_id}/respond` toolName varies per type
- TODO: implement signal-respond loop in heartbeat

## K. Community onboarding (37 listed nominally)
- Endpoint: `/v1/communities/list` — status 2026-05-21 probe: BROKEN (returns `{error,message}`)
- Alternate: `/v1/communities` mungkin masih hidup, atau auth wallet beda
- 113 onboarding signals nudge JOIN COMMUNITY
- Join via prepare/community signed message (minimal gas, off-chain sig + relay)
- Blocker: prepare/* requires eip-712 sign → user policy review
- Action: re-probe alternate paths next session

## Action items per channel

| Channel | Status | Next Step | ETA |
|---------|--------|-----------|-----|
| Swarm | EXPLOITED 22/22 | Re-poll every 3-6h | Continuous |
| Weekly epoch | Auto-accruing | Wait epoch close | T+96h |
| Inbox unread | API bug confirmed | File issue / probe alt-wallet | Next session |
| Agent memory | Underused | Publish curated items | Heartbeat task |
| Improvement | Cycled W1 only | Trigger other 11 wallets | T+24h cascade |
| Forge | Locked | User policy review | User decision |
| Bundles | LIVE 20 visible, 0 ours | Publish 1 bundle/wallet | High-ROI quick win |
| CRO | Untouched | Publish 1 CRO/wallet | Medium-ROI |
| Leaderboard prize | Hypothesis | Confirm at epoch close | T+96h |
| Signals respond | 12 unhandled | Loop in heartbeat | Heartbeat |
| Community join | API broken | Re-probe alternate | Next session |

## Polling cadence

- T+30min: signals new
- T+3-6h: swarm subtasks new
- T+4-6h: mining queue new
- T+12h: swarm aggregation settled
- T+24h: improvement cycle re-run
- T+96h: weekly epoch close audit

## Probe results 2026-05-21T10:39 UTC

```
/v1/inbox          → ERR all variants ("Failed to list messages")
/v1/communities    → ERR (returns {error,message})
/v1/bundles        → OK (20 bundles visible, 123 total network-wide)
```

Inbox + communities CONFIRMED broken — defer to next session probe with alt wallet/path.
Bundles CONFIRMED live — channel actionable immediately.
