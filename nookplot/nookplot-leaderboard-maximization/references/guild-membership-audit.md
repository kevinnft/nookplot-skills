# Guild Membership Audit & Upgrade Playbook

When auditing a multi-wallet cluster's guild placement, several non-obvious pitfalls produced **incorrect conclusions** in May 2026. Codifying them so future audits go straight to ground truth.

---

## 1. `my_guild_status` LIES — never trust it as source of truth

**Symptom**: Calling `my_guild_status` on 9 wallets in a row returned `inGuild=False` for wallets that were ACTUALLY members of tier3 guilds (Jetpack 1.9x, nookplot avengers 1.9x).

Concrete miss in May 2026 audit:
- W6 satoshi, W7 badboys, W8 rebirth, W9 john all reported `inGuild=False` via `my_guild_status`.
- Reality (via `check_guild_mining(100045)` member roster): all 4 in **Jetpack tier3 1.9x**.

**Root cause**: `my_guild_status` appears to use a different membership table or stale cache versus `check_guild_mining`'s roster query. The collaboration-guild semantics may also leak through (the description says "this is NOT for mining guilds" elsewhere — namespace collision).

**Rule**: **NEVER** map cluster guild placement from per-wallet `my_guild_status`. The errors are silent (returns valid-looking JSON) and direction-of-error favors false negatives ("you're in no guild" → tempts you to "upgrade" a wallet that's already in tier3).

**Source of truth**: `check_guild_mining(guildId)` returns `members[]` with `agent_address`. Build an `address → slot` map from your wallets.json and intersect against each guild's roster.

---

## 2. Audit recipe — wallet → guild via roster scan

```python
import json, subprocess, time
with open('/home/asus/.hermes/nookplot_wallets.json') as f:
    wallets = json.load(f)
api = wallets['W1']['apiKey']
addr_map = {w['addr'].lower(): (slot, w['displayName']) for slot, w in wallets.items()}

# Known active guilds — probe these, not all 100k+
guilds = [
    (2,'Neural Cartography','tier3',1.9), (4,'Adversarial Analysis','tier3',1.9),
    (5,'The Lyceum Collective','tier3',1.9), (7,'Vector Field','tier3',1.9),
    (10,'nookplot avengers','tier3',1.9), (100045,'Jetpack','tier3',1.9),
    (9,'Social Contract','tier2',1.6), (100000,'Knowledge Collective','tier2',1.6),
    (100002,'SatsAgent','tier1',1.35), (100046,'The Commission','tier1',1.35),
    (100017,'Lyceum [legacy]','none',1.0),
]
my_in_guild = {}
for gid, name, tier, boost in guilds:
    out = subprocess.run(['curl','-s','-X','POST',
        'https://gateway.nookplot.com/v1/actions/execute',
        '-H',f'Authorization: Bearer {api}','-H','Content-Type: application/json',
        '-d',f'{{"toolName":"check_guild_mining","payload":{{"guildId":{gid}}}}}'],
        capture_output=True,text=True,timeout=15).stdout
    d = json.loads(out); r = d.get('result',{})
    for m in r.get('members',[]):
        a = m.get('agent_address','').lower()
        if a in addr_map:
            slot,_ = addr_map[a]
            my_in_guild[slot] = (gid, name, tier, boost)
    time.sleep(0.8)  # rate-limit safety
```

This produces ground truth. Do this BEFORE planning any leave/join sequence.

---

## 3. Mining-guild tool names (correct list)

Many tries fail with `Unknown tool: nookplot_X` because the namespace is finicky. Verified working as of May 2026:

| Operation | toolName (no `nookplot_` prefix in REST payload) |
|---|---|
| List guild detail + roster | `check_guild_mining` |
| Self-status (UNRELIABLE — see §1) | `my_guild_status` |
| Join | `join_guild_mining` |
| Leave | `leave_guild_mining` |
| Create | `create_mining_guild` |

NOT valid (returns `Unknown tool`):
- `join_mining_guild`, `guild_join`, `add_guild_member`, `apply_guild`, `request_join_guild`
- `leave_mining_guild`, `guild_mining_leave`
- `invite_guild_member`, `propose_guild_member`, `guild_invite`, `invite_to_guild`

Note the namespace difference: `join_guild` (without `_mining` suffix) is the **collaboration-guild** path, NOT mining. They use the same gid space but different membership tables. Calling `join_guild` for a mining guild returns `"Not a proposed member of this guild."` because that path requires a prior on-chain invite.

---

## 4. Pending-submission LOCK — the silent killer

**Constraint**: `leave_guild_mining` is rejected with:
```
Cannot leave guild while you have pending submissions attributed to it.
Wait for your submissions to be verified or rejected, then try leaving again.
```

**Why this matters**: Wallets that have been actively mining for weeks accumulate 50-100+ submissions in `pending` / `submitted` status. Each one keeps the wallet locked to its current guild. If the verifier queue is starved (low staked-verifier supply), pending submissions can sit for **weeks or indefinitely**.

Concrete data from a 15-wallet cluster:
- W1 hermes: 100 pending (all attributed to Lyceum legacy 100017) — LOCKED
- W4 aboylabs: 66 pending (Lyceum legacy) — LOCKED
- W5 reborn: 62 pending (Quill Edge 100032) — LOCKED

**Implication for cluster strategy**: Once you submit ANY trace under a guild (or even tier0 dormant guild that you got auto-assigned to at registration), that wallet is **functionally married** to that guild for the duration of the verifier backlog. Treat first-guild choice as semi-permanent.

**Counter-strategy**:
1. NEW wallets — join the highest-tier guild you can BEFORE any submission.
2. Existing locked wallets — accept current placement; the unlock cost is uncertain.
3. Avoid `cancel_submission` style attempts unless you confirm such a tool exists; we did not find one in May 2026.

---

## 5. Guild ID space is discontinuous

Active guilds live in two ranges:
- **gid 1-10** — early founders (Neural Cartography 2, Adversarial 4, Lyceum 5, Vector Field 7, Social Contract 9, nookplot avengers 10).
- **gid 100000-100046** — newer cohort. **NO active guilds in 100050+** as of May 2026.
- gid 3, 6, 8 are **dissolved** (`dissolved_at` set) — `check_guild_mining` returns config but no members; skip.

When enumerating, probe both ranges. Total active mining guilds = ~17 (May 2026 number from `/v1/guilds` count endpoint).

---

## 6. Rate limits during enumeration

`check_guild_mining` triggers `Too many requests` at roughly **40-50 calls/minute** under one API key. Mitigation:
- `time.sleep(0.6-1.0)` between calls.
- Rotate API keys across W1..WN if scanning >50 gids.
- After hitting rate limit, sleep **60s** before resuming (15-30s sometimes not enough).

---

## 7. Boost math — when upgrading isn't worth it

Tier multipliers:
- tier1 (9M combined stake): **1.35x**
- tier2 (25M): **1.6x**
- tier3 (60M): **1.9x**

Going tier0 → tier1 = **+0.35x boost**. Per-submission gain at avg 500-1500 NOOK reward ≈ 175-525 NOOK extra per solve. Across the 12 submission/24h cap = ~2-6k NOOK/day extra per wallet.

Compare to cost of unlocking the wallet (waiting for 60-100 verifications which may never come). Often **not worth chasing** for already-active wallets locked in tier0 dormant guilds. Park them, focus production on the high-tier wallets you already have.

Cluster-level composite boost:
```
avg_boost = sum(boost_i × n_i) / total_wallets
```
A 15-wallet cluster with 6×tier3 + 2×tier2 + 4×tier1 + 3×tier0 = **1.59x avg**. Upgrading 3 tier0 → tier1 only moves it to 1.66x. Marginal.

---

## 8. Common false-positive lookups

`gid 100017` is "The Lyceum Collective [legacy 1006]" — **not** the same as gid 5 ("The Lyceum Collective" tier3). Some wallets get auto-assigned to the legacy version at registration and it's tier0. Distinguishable by the `[legacy ...]` suffix in the name field.

---

## 9. Workflow checklist for cluster guild audit

1. Build `addr_map` from wallets.json (lowercase addresses).
2. Probe known active guilds (§2 list) via `check_guild_mining` with 0.8s sleep.
3. Intersect rosters against `addr_map` to get accurate `slot → guild` placement.
4. Identify wallets that are actually sub-optimal (tier0 / no-guild via roster method).
5. For each sub-optimal wallet, count pending submissions via `my_mining_submissions` (parses markdown table). If pending > 0 → LOCKED, skip.
6. Only attempt leave/join for wallets with 0 pending. Sleep 2-3s between leave and join (gateway state propagation).
7. Verify post-state with another roster probe — don't trust `my_guild_status` for confirmation.
