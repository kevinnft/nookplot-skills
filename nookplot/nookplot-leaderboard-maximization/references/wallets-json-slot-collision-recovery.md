# wallets.json Slot Collision — Detection and Recovery

When the user adds a new wallet (W_N+1) but the bootstrap script writes it into an EXISTING slot, the previous occupant of that slot gets silently overwritten. The user catches this later because the displayName at slot W_N doesn't match what they remember creating.

This file documents (1) how to detect it, (2) how to recover non-destructively, (3) how to prevent it on next bootstrap.

---

## How it happens

`~/.hermes/nookplot_wallets.json` is a flat dict keyed `W1..WN`. Bootstrap scripts that pick the new slot via `f"W{len(wallets)+1}"` are correct ONLY when the keyset is contiguous starting at 1. If a slot is ever deleted, or if a write happens during a partial state, `len(wallets)+1` collides with an existing key.

Concrete case observed 2026-05-19 → 2026-05-20:
- Session A (May 19 ~23:40 WIB) created W11=WhiteAgent (0xcdDb0f53...390BDe).
- Session B (later same evening) created PanuMan via `wallets["W"+str(len(wallets)+1)] = …`. At the moment that ran, the in-memory snapshot was 11 keys → `len+1=12` should have been correct, BUT the script actually used the WALLETS dict size at that moment which still resolved to 11 (race or earlier-snapshot variable), so it wrote `wallets["W11"] = PanuMan`, clobbering WhiteAgent.
- Memory entry was updated to record `W11 PanuMan tier3 guild #10`, hiding the loss.
- Detection only happened the next session when the user said "W11 WhiteAgent ada wallet 11 ini, panuman itu wallet 12".

## Detection signals

Audit `wallets.json` against memory + filesystem traces before trusting the file:

```bash
# 1. Inspect every backup that lives in ~/.hermes/ and ~/.hermes/backups/
for f in ~/.hermes/nookplot_wallets.json.bak.* ~/.hermes/backups/nookplot_wallets*.bak; do
  [ -e "$f" ] || continue
  echo "=== $f ==="
  python3 -c "import json,sys; d=json.load(open('$f')); [print(f'{k}: {d[k][\"displayName\"]:20s} {d[k][\"addr\"]}') for k in sorted(d, key=lambda x:int(x[1:]))]"
done
```

Smoking gun: a backup that has `W11=WhiteAgent` but the live file has `W11=PanuMan`. That delta is the overwrite.

Other signals worth running:
- Check `~/.hermes/sessions/*.json` for the bootstrap session (`grep -l "displayName.*WhiteAgent" sessions/*.json`). Recover the address from the session log if no backup survived.
- Check `/tmp/w*_creds.json` files; the staging files are mode 600 and usually still on disk.
- `ls /tmp/w*_creds.json` will reveal orphaned wallets — credentials without a matching entry in `wallets.json`.

## Recovery (non-destructive)

NEVER rewrite the live file in place without a backup. Procedure that worked for the WhiteAgent / PanuMan case:

```python
import json, time, shutil, os

CUR = "/home/asus/.hermes/nookplot_wallets.json"
BAK_OLD = "/home/asus/.hermes/nookplot_wallets.json.bak.<timestamp>"  # the one that still has WhiteAgent

# 1. Backup current first (which has the wrong W11=PanuMan)
ts = int(time.time())
backup_path = f"/home/asus/.hermes/backups/nookplot_wallets_pre_w12fix_{ts}.json.bak"
shutil.copy(CUR, backup_path)
os.chmod(backup_path, 0o600)

# 2. Load both and merge
cur = json.load(open(CUR))
old = json.load(open(BAK_OLD))

panuman    = cur["W11"]   # currently mislabeled
whiteagent = old["W11"]   # the real W11

# Sanity check before swapping — don't proceed if the data shape is unexpected
assert panuman["displayName"] == "PanuMan",    f"unexpected current W11: {panuman['displayName']}"
assert whiteagent["displayName"] == "WhiteAgent", f"unexpected backup W11: {whiteagent['displayName']}"

merged = {k: cur[k] for k in cur}
merged["W11"] = whiteagent
merged["W12"] = panuman

with open(CUR, "w") as f:
    json.dump(merged, f, indent=2)
os.chmod(CUR, 0o600)
```

Then verify:

```python
verify = json.load(open(CUR))
for k in sorted(verify, key=lambda x:int(x[1:])):
    w = verify[k]
    print(f"  {k:4s} | {w['displayName']:22s} | {w['addr']}")
```

Update memory + Mnemosyne immediately so the next session sees `cluster=12 wallets` not 11. Both stores need the correction; daily-memory alone won't propagate fast enough.

## Prevention — bootstrap script must use max-key, not len-key

Wrong:
```python
new_slot = f"W{len(wallets) + 1}"
wallets[new_slot] = new_wallet  # clobbers if keyset is non-contiguous OR stale snapshot
```

Right (always picks an unused slot):
```python
existing_indices = [int(k[1:]) for k in wallets if k.startswith("W") and k[1:].isdigit()]
new_slot = f"W{(max(existing_indices) + 1) if existing_indices else 1}"
assert new_slot not in wallets, f"slot {new_slot} already occupied — refusing to overwrite"
wallets[new_slot] = new_wallet
```

Also: re-read `wallets.json` from disk RIGHT BEFORE the write. Cached `WALLETS` constant at the top of `np_signer.py` or any helper is a stale-snapshot risk if multiple sessions touch the file in the same hour.

## Cross-link

The on-chain side of the wallet is fine — `prepare/register` + `relay` minted the WhiteAgent agent record under its real address. The collision is purely a local bookkeeping bug. No on-chain rollback needed; just fix the JSON map and proceed.
