#!/usr/bin/env bash
# recover_wallet_keys.sh — recover Nookplot wallet apiKeys from local artifacts.
#
# Use when ~/.hermes/nookplot_wallets.json has masked apiKeys ("***") AND
# /tmp/wN_creds.json files are missing (laptop sleep / reboot wiped /tmp).
#
# Sources scanned (in priority order):
#   1. ~/.hermes/state.db (sqlite messages table — past tool-call arguments)
#   2. ~/.hermes/ recursive grep (excluding node_modules)
#   3. ~/.env
#
# Each candidate is verified against gateway.nookplot.com/v1/agents/me.
# Working keys are matched to displayNames and written back into
# ~/.hermes/nookplot_wallets.json.
#
# Usage: bash scripts/recover_wallet_keys.sh
#        (no args, idempotent, only updates fields that are currently masked)

set -euo pipefail

CONSOLIDATED="$HOME/.hermes/nookplot_wallets.json"
GATEWAY="https://gateway.nookplot.com"
TMP_KEYS="$(mktemp)"
trap "rm -f $TMP_KEYS" EXIT

echo "[recover] harvesting candidate nk_ keys..."

# Source 1: state.db messages table
if command -v sqlite3 >/dev/null 2>&1 && [[ -f "$HOME/.hermes/state.db" ]]; then
  sqlite3 "$HOME/.hermes/state.db" "SELECT * FROM messages" 2>/dev/null \
    | grep -oE 'nk_[A-Za-z0-9_-]{60,70}' >> "$TMP_KEYS" || true
fi

# Source 2: ~/.hermes recursive grep (skip node_modules + dbs)
grep -rho 'nk_[A-Za-z0-9_-]\{60,70\}' "$HOME/.hermes/" 2>/dev/null \
  | grep -v '^nk_$' >> "$TMP_KEYS" || true

# Source 3: ~/.env
if [[ -f "$HOME/.env" ]]; then
  grep -oE 'nk_[A-Za-z0-9_-]{60,70}' "$HOME/.env" >> "$TMP_KEYS" || true
fi

# Filter to exactly 67 chars (shorter = truncated prefix)
UNIQUE_KEYS=$(awk 'length($0) == 67' "$TMP_KEYS" | sort -u)
COUNT=$(echo "$UNIQUE_KEYS" | grep -c . || true)
echo "[recover] found $COUNT unique 67-char candidates"

# Verify each candidate against gateway
declare -A NAME_TO_KEY
declare -A NAME_TO_ADDR
while IFS= read -r KEY; do
  [[ -z "$KEY" ]] && continue
  RESP=$(curl -fs -H "Authorization: Bearer $KEY" "$GATEWAY/v1/agents/me" 2>/dev/null || echo "")
  if [[ -n "$RESP" ]]; then
    NAME=$(echo "$RESP" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("displayName","") or "")' 2>/dev/null || echo "")
    ADDR=$(echo "$RESP" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("address","") or "")' 2>/dev/null || echo "")
    if [[ -n "$NAME" ]]; then
      echo "[recover]   ${KEY:0:18}... -> $NAME ($ADDR)"
      NAME_TO_KEY[$NAME]=$KEY
      NAME_TO_ADDR[$NAME]=$ADDR
    fi
  fi
done <<< "$UNIQUE_KEYS"

# Write back to consolidated JSON
if [[ ! -f "$CONSOLIDATED" ]]; then
  echo "[recover] no consolidated file — creating $CONSOLIDATED"
  echo '{}' > "$CONSOLIDATED"
  chmod 600 "$CONSOLIDATED"
fi

python3 - <<PY
import json, os
path = "$CONSOLIDATED"
with open(path) as f:
    cfg = json.load(f)
label_map = {"hermes":"W1","9dragon":"W2","kevinft":"W3","aboylabs":"W4","reborn":"W5"}
keys = {
$(for name in "${!NAME_TO_KEY[@]}"; do
    echo "  \"$name\": (\"${NAME_TO_KEY[$name]}\", \"${NAME_TO_ADDR[$name]}\"),"
done)
}
updated = 0
for name, (k, addr) in keys.items():
    L = label_map.get(name)
    if not L:
        continue
    if L not in cfg:
        cfg[L] = {"displayName": name, "addr": addr, "apiKey": k}
        updated += 1
        continue
    if cfg[L].get("apiKey", "") in ("", "***", None) or len(cfg[L].get("apiKey","")) < 60:
        cfg[L]["apiKey"] = k
        updated += 1
    cfg[L].setdefault("displayName", name)
    cfg[L].setdefault("addr", addr)
with open(path, "w") as f:
    json.dump(cfg, f, indent=2)
os.chmod(path, 0o600)
print(f"[recover] {updated} wallet entries updated in {path}")
PY

echo "[recover] done."
