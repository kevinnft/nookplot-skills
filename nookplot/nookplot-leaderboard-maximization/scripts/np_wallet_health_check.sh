#!/usr/bin/env bash
# Nookplot 5-wallet health check and auto-repair
# Run on demand. Restores canonical from backups if missing.
# Usage: ~/.hermes/scripts/np_wallet_health_check.sh
# Exits 0 if all 5 wallets healthy, 1 if missing+no backup, 2 if any wallet bad.

CANON=~/.hermes/nookplot_wallets.json
BAK1=~/.hermes/backups/nookplot_wallets.json.bak
BAK2=~/nookplot_wallets.json.bak

restore_from() {
  if [ -f "$1" ]; then
    cp "$1" "$CANON"
    chmod 600 "$CANON"
    echo "RESTORED $CANON from $1"
    return 0
  fi
  return 1
}

if [ ! -f "$CANON" ]; then
  echo "MISSING canonical $CANON, attempting restore..."
  restore_from "$BAK1" || restore_from "$BAK2" || {
    echo "FATAL: no backups available, recover via state.db grep + curl /v1/agents/me"
    echo "  grep -rho 'nk_[A-Za-z0-9_-]\\{60,70\\}' ~/.hermes/state.db | sort -u | awk 'length(\$0)==67'"
    exit 1
  }
fi

python3 - <<'PY'
import json, sys
try:
    with open('/home/asus/.hermes/nookplot_wallets.json') as f:
        d = json.load(f)
except Exception as e:
    print(f"PARSE-FAIL: {e}")
    sys.exit(1)

ok = 0
expected = {"W1":"hermes","W2":"9dragon","W3":"kevinft","W4":"aboylabs","W5":"reborn"}
for k, expected_name in expected.items():
    w = d.get(k, {})
    name = w.get('displayName')
    apikey = w.get('apiKey','')
    addr = w.get('addr','')
    has_full = isinstance(apikey, str) and apikey.startswith('nk_') and len(apikey) == 67
    has_addr = isinstance(addr, str) and addr.startswith('0x') and len(addr) == 42
    if name == expected_name and has_full and has_addr:
        ok += 1
        print(f"  OK {k} {name} {addr[:10]}...")
    else:
        print(f"  BAD {k} {name or '?'} apikey={'OK' if has_full else 'BAD'} addr={'OK' if has_addr else 'BAD'}")
print(f"\n{ok}/5 wallets healthy")
sys.exit(0 if ok == 5 else 2)
PY
