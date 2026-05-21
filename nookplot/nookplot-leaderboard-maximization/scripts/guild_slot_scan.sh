#!/usr/bin/env bash
# Re-runnable mining-guild slot scan — answers "cek slot guild tier tertinggi"
# Reads any working API key from ~/.hermes/nookplot_wallets.json and prints a
# tier-grouped table of joinable guilds with slot counts, stake, domains, earned.
#
# Usage:
#   bash ~/.hermes/skills/nookplot/nookplot-leaderboard-maximization/scripts/guild_slot_scan.sh
#
# No state mutation, safe to run repeatedly. Pure read.

set -euo pipefail

WALLETS_JSON="${HOME}/.hermes/nookplot_wallets.json"
if [[ ! -f "${WALLETS_JSON}" ]]; then
  echo "ERROR: ${WALLETS_JSON} missing" >&2
  exit 2
fi

# Pick first wallet whose apiKey looks complete (>=60 chars). Truncated keys
# in the canonical file are a known artifact — see SKILL.md "Trap (confirmed
# May 17 2026)" for full key recovery via grep on ~/.hermes/.
KEY=$(python3 - <<'PY'
import json, sys, os, glob, re
path = os.path.expanduser("~/.hermes/nookplot_wallets.json")
data = json.load(open(path))
for w in ("W2","W1","W3","W4","W5","W6"):
    k = data.get(w,{}).get("apiKey","")
    if k.startswith("nk_") and len(k) >= 60:
        print(k); sys.exit(0)
# fall back: scan ~/.hermes for any full-length key
for f in glob.glob(os.path.expanduser("~/.hermes/**/*"), recursive=True):
    try:
        with open(f, errors="ignore") as fh:
            m = re.search(r'nk_[A-Za-z0-9_-]{60,70}', fh.read())
            if m:
                print(m.group(0)); sys.exit(0)
    except Exception:
        pass
sys.exit(3)
PY
)

API="https://gateway.nookplot.com"

JOIN=$(curl -s -H "Authorization: Bearer ${KEY}" "${API}/v1/mining/guilds/joinable?limit=200")
LB=$(curl -s -H "Authorization: Bearer ${KEY}" "${API}/v1/mining/guilds/leaderboard?limit=200")

python3 - <<PY
import json
join = json.loads('''${JOIN}''')["guilds"]
lb_list = json.loads('''${LB}''')["guilds"]
lb = {g["guild_id"]: g for g in lb_list}

tier_rank = {"tier3": 3, "tier2": 2, "tier1": 1, "none": 0}
join.sort(key=lambda g: (-tier_rank.get(g["tier"],0), g["patronCount"]))

print(f"{'Tier':<7} {'Boost':<6} {'ID':<8} {'Slots':<7} {'Stake':<14} {'Earned':<14} {'Name':<32} {'Domains'}")
print("-"*180)
boost_map = {"tier3":"1.9x","tier2":"1.6x","tier1":"1.35x","none":"1.0x"}
for g in join:
    if g["tier"] not in ("tier1","tier2","tier3"):
        continue
    full = lb.get(g["id"], {})
    domains = ",".join(full.get("domain_specializations", [])[:5])
    if len(full.get("domain_specializations", [])) > 5: domains += "..."
    slots = f'{g["patronCount"]}/6'
    stake = f'{int(g.get("totalStake",0)):,}'
    earned = f'{full.get("total_guild_earned",0):,.0f}'
    print(f'{g["tier"]:<7} {boost_map[g["tier"]]:<6} {g["id"]:<8} {slots:<7} {stake:<14} {earned:<14} {g["name"][:30]:<32} {domains}')

# Also list FULL tier3 for context (these are 1.9x targets but always taken)
print()
print("FULL tier3 (for context, normally always 6/6):")
for g in lb_list:
    if g["mining_tier"] == "tier3" and g["member_count"] >= 6:
        print(f'  id={g["guild_id"]} {g["name"]} stake={g["total_stake"]:,.0f} earned={g["total_guild_earned"]:,.0f}')
PY
