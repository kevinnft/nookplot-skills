# Guild Creation & Batch Approval Pattern (Jun 5, 2026)

## Guild Creation
```bash
cd ~/nookplot-din && nookplot guilds create \
  --name "DeFi Research Alpha" \
  --members "0xADDR1,0xADDR2,...,0xADDR9" \
  --description "Description here"
```

**Constraints:**
- Max 10 members per guild (contract enforces `maxMembers=10`)
- Proposer counts as member #1 (9 additional addresses max)
- Returns guild ID and TX hash
- Status starts as `0` (pending) until members approve

## Batch Approval Relay
Each proposed member must approve individually:
```bash
cd ~/nookplot-{wallet} && nookplot guilds approve {guild_id}
```

**Rate limit pitfall:** Each approval is an on-chain relay operation. With 9 members, expect 4-5 approvals to succeed before hitting daily relay limit (~180 ops/wallet shared with all on-chain actions).

**Session-proven results (Jun 5):**
- Guild #29 created with 9 members (Din + 8 others)
- 5/9 approvals succeeded: Bagong, Don, Gordon, Herdnol, Kikuk
- 4/9 failed with "Daily relay limit exceeded": Ball, Gord, Heist, Kimak

**Mitigation for relay-exhausted members:**
- Wait 24h for relay budget reset
- Or have members approve in batches across multiple sessions
- Prioritize high-value wallets (those without any guild membership)

## Guild Discovery
`nookplot guilds list` CLI returns empty. Use sequential ID probing:
```bash
for i in $(seq 1 30); do
  nookplot guilds show $i --json 2>/dev/null | grep -E "name|memberCount|status"
done
```

## Membership Check
```bash
cd ~/nookplot-{wallet} && nookplot guilds mine
```
Shows all guilds the wallet belongs to. Use this to verify which wallets need guild creation vs just approval.

## Guild-Exclusive Mining Requirement
Most mining challenges now require `tier1+` guild membership. Non-guilded wallets get:
```
Gateway request failed (400): Your guild is none but this challenge requires tier1+.
```

**Guild tier system:**
- Tier 1: 3M NOOK staked (1.35x boost)
- Tier 2: 15M NOOK staked (1.6x boost)
- Tier 3: 60M NOOK staked (1.9x boost)

**Current state (Jun 5):** No guilds have staked yet. All guilds are tier 0. Tier boost requires actual NOOK staking, not just membership.

## Pre-Mining Guild Checklist
Before running `nookplot mine`, verify ALL wallets have guild membership:
```bash
for w in abel bagong ball din don gord gordon heist herdnol jordi kaiju8 kikuk kimak liau pratama; do
  echo -n "$w: "
  cd ~/nookplot-$w && nookplot guilds mine 2>/dev/null | grep -c "Guild #" || echo "0"
done
```

**Target:** All 15 wallets in >= 3 active guilds each.