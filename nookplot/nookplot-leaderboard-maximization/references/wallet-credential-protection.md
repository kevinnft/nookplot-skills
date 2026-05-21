# Wallet Credential Protection — 5-Layer Defense

When the user says "simpan baik2 wallet" / "jangan sampai hilang" / "ingat di
semua sesion berikutnya" they want durable, multi-layer protection against
credential loss between sessions (laptop sleep wipes /tmp, file corruption,
accidental delete). One persistent file is not enough.

## The 5-layer pattern

```
LAYER  LOCATION                                          MODE   ROLE
1      ~/.hermes/nookplot_wallets.json                   600    canonical source of truth
2      ~/.hermes/backups/nookplot_wallets.json.bak       600    on-disk backup #1 (hermes dir)
3      ~/nookplot_wallets.json.bak                       600    on-disk backup #2 (home dir)
4      Mnemosyne global memory entry (importance 0.98)   -      address+identity recall across sessions
5      ~/.hermes/scripts/np_wallet_health_check.sh       +x     auto-restore script
```

Why five: any one layer can fail (file corruption, disk fill, memory eviction,
script broken). The user signal "jangan sampai hilang" justifies the redundancy.

## Setup procedure

```bash
# 1. Verify canonical is healthy first
python3 -c "import json; d=json.load(open('/home/asus/.hermes/nookplot_wallets.json')); \
  [print(k, w['displayName'], len(w.get('apiKey',''))) for k,w in d.items()]"

# 2. Create backups (mode 600, owner-only)
mkdir -p ~/.hermes/backups
chmod 700 ~/.hermes/backups
cp ~/.hermes/nookplot_wallets.json ~/.hermes/backups/nookplot_wallets.json.bak
cp ~/.hermes/nookplot_wallets.json ~/nookplot_wallets.json.bak
chmod 600 ~/.hermes/backups/nookplot_wallets.json.bak ~/nookplot_wallets.json.bak

# 3. Mnemosyne — store full wallet inventory at high importance, scope=global
#    veracity=stated, importance=0.98
#    Include: addr, displayName, guild assignment, file path, sha256 prefix.
#    DO NOT put full apiKey or pk in mnemosyne — addresses + identity only.

# 4. Memory legacy: short pointer entry referencing canonical file path,
#    backup paths, recovery procedure. The full secrets stay on disk.

# 5. Health check script — see scripts/np_wallet_health_check.sh
```

## Health check script (canonical lives in scripts/np_wallet_health_check.sh)

The script:
- Checks canonical file exists; restores from BAK1 → BAK2 if missing
- Validates each wallet has 67-char `nk_...` apiKey and 42-char `0x...` addr
- Reports per-wallet OK / BAD, exits 0 only if all 5 healthy

Run on demand or wire into a session-start hook.

## Recovery procedure (when canonical AND backups all gone)

This is the worst case — laptop wiped, /tmp gone, backups deleted. Keys are
recoverable from `~/.hermes/state.db` (sqlite messages table) which preserves
historical tool-call arguments including every apiKey ever used.

```bash
# 1. Grep all 67-char nk_ keys from state.db
grep -rho 'nk_[A-Za-z0-9_-]\{60,70\}' ~/.hermes/state.db | sort -u | \
  awk 'length($0)==67' > /tmp/candidate_keys.txt

# 2. For each candidate, validate via gateway
while read key; do
  result=$(curl -s -H "Authorization: Bearer $key" \
    https://gateway.nookplot.com/v1/agents/me)
  name=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('displayName','BAD'))")
  addr=$(echo "$result" | python3 -c "import sys,json; print(json.load(sys.stdin).get('address','BAD'))")
  echo "$key|$name|$addr"
done < /tmp/candidate_keys.txt
```

This recovers apiKey + addr per displayName. Private keys are NOT recoverable
from state.db (never echoed). For pk loss, last resort is manual web reconnect
at `nookplot.com/join` — re-issues a fresh apiKey but the address stays the same.

## Persistent identity vs persistent secrets

Memory split:
- **Mnemosyne global**: addresses, displayNames, guild assignments, file paths,
  sha256 prefix, recovery procedure. SAFE to recall in any session.
- **Memory legacy**: short pointer referencing canonical paths + recovery hint.
  The legacy memory is read on every turn — keep it compact.
- **Disk file (mode 600)**: actual apiKey + pk. Never echoed in conversation.

When the user references "wallet recovery" or "lost the file" in a future
session, the agent should:
1. Run `~/.hermes/scripts/np_wallet_health_check.sh` first (auto-restore)
2. If that fails, check mnemosyne for the wallet inventory
3. Last resort: state.db grep → curl validation pattern above

## Filename convention pitfall

The /tmp/wN_creds.json files have SWAPPED labels relative to wallet IDs:
- `/tmp/w3_creds.json` contains W4 aboylabs
- `/tmp/w4_creds.json` contains W3 kevinft
- `/tmp/w5_creds.json` contains W5 reborn

This is historical convention — do not "fix" the naming, downstream scripts
read by filename. The canonical `~/.hermes/nookplot_wallets.json` uses correct
W1-W5 labels keyed by displayName, so always prefer the canonical file when
loading wallets in fresh code.

## Mnemosyne entry shape (recommended)

```
service: nookplot
scope: global
importance: 0.95-0.98
veracity: stated
content: |
  Nookplot 5-wallet cluster:
  - W1 hermes 0x5fcF1aE1... (MCP, no pk)
  - W2 9dragon 0x5b82be85... (~/.env)
  - W3 kevinft 0xDf5bc41E... (recovered via web UI YYYY-MM-DD)
  - W4 aboylabs 0xdbAFE90B...
  - W5 reborn 0xd01767C9...
  Canonical: ~/.hermes/nookplot_wallets.json (mode 600, sha256 prefix XXXXXXXX)
  Backups: ~/.hermes/backups/, ~/nookplot_wallets.json.bak (both 600)
  Health check: ~/.hermes/scripts/np_wallet_health_check.sh
  Recovery if all gone: grep state.db for nk_ keys → curl /v1/agents/me to identify
```

The sha256 prefix lets a future session detect file tampering — if the prefix
in mnemosyne disagrees with the actual file hash, something modified the
canonical and the backups should be cross-checked.
