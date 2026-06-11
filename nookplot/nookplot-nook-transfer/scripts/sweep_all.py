"""
Nookplot NOOK Token Full Sweep Script
Usage: ~/.hermes/hermes-agent/venv/bin/python sweep_all.py <DEST_ADDRESS>

Multi-pass sweep: transfers all NOOK from every wallet to destination,
then verifies all balances are 0. Re-sweeps any wallet that received
new rewards during the transfer process.

Run with the Hermes venv (has eth_account):
  ~/.hermes/hermes-agent/venv/bin/python sweep_all.py 0xb1caec6d...
"""
import json, subprocess, sys, time
from eth_account import Account

BASE_RPC = "https://mainnet.base.org"
NOOK_TOKEN = "0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3"
CHAIN_ID = 8453
WALLETS_PATH = "/home/asus/.hermes/nookplot_wallets.json"
MAX_PASSES = 5  # safety limit

if len(sys.argv) < 2:
    print("Usage: sweep_all.py <DEST_ADDRESS>")
    sys.exit(1)

DEST = sys.argv[1].lower()
if not DEST.startswith("0x") or len(DEST) != 42:
    print("ERROR: Invalid destination address: " + DEST)
    sys.exit(1)

wallets = json.loads(open(WALLETS_PATH).read())

def rpc_call(method, params=None):
    payload = json.dumps({"jsonrpc":"2.0","method":method,"params":params or [],"id":1})
    r = subprocess.run(["curl","-s","--max-time","15","-X","POST",BASE_RPC,
        "-H","Content-Type: application/json","-d",payload],
        capture_output=True, text=True, timeout=20)
    try:
        resp = json.loads(r.stdout)
        if "error" in resp: return None, resp["error"]
        return resp.get("result"), None
    except Exception as e:
        return None, str(e)

def get_nook_balance(addr):
    padded = addr[2:].lower().zfill(64)
    result, err = rpc_call("eth_call", [{"to": NOOK_TOKEN, "data": "0x70a08231" + padded}, "latest"])
    if err: return 0
    return int(result, 16) if result and result != "0x" else 0

def get_nonce(addr):
    result, err = rpc_call("eth_getTransactionCount", [addr, "latest"])
    return int(result, 16) if result else None

def get_gas_price():
    result, err = rpc_call("eth_gasPrice")
    return int(result, 16) if result else 6000000

def build_transfer_calldata(to_addr, amount_wei):
    to_padded = to_addr[2:].lower().zfill(64)
    amount_padded = hex(amount_wei)[2:].zfill(64)
    return "0xa9059cbb" + to_padded + amount_padded

def sweep_pass(wallets, gas_price, pass_num):
    sent = 0
    total_sent = 0
    for wid in sorted(wallets.keys(), key=lambda x: int(x[1:])):
        w = wallets[wid]
        addr = w["addr"]; pk = w["pk"]
        nook_raw = get_nook_balance(addr)
        if nook_raw == 0:
            time.sleep(0.3)
            continue
        nook_fmt = nook_raw / 1e18
        nonce = get_nonce(addr)
        if nonce is None:
            print("[Pass %d] %s ERROR: nonce fetch failed" % (pass_num, wid))
            continue
        calldata = build_transfer_calldata(DEST, nook_raw)
        tx = {"to": NOOK_TOKEN, "value": 0, "gas": 100000,
              "gasPrice": gas_price, "nonce": nonce,
              "data": calldata, "chainId": CHAIN_ID}
        account = Account.from_key(pk)
        signed = account.sign_transaction(tx)
        raw_tx = "0x" + signed.raw_transaction.hex()
        tx_hash, err = rpc_call("eth_sendRawTransaction", [raw_tx])
        if err:
            print("[Pass %d] %s ERROR: %s" % (pass_num, wid, err))
        else:
            sent += 1
            total_sent += nook_fmt
            print("[Pass %d] %s SENT %.4f NOOK  tx: %s" % (pass_num, wid, nook_fmt, tx_hash))
        time.sleep(1.5)
    return sent, total_sent

# === MAIN ===
print("=== NOOK FULL SWEEP ===")
print("Destination: " + DEST)
print("Token: " + NOOK_TOKEN)
print("Chain: Base (8453)")
print("")

# Initial balance check
print("--- Balance Check ---")
total_initial = 0
for wid in sorted(wallets.keys(), key=lambda x: int(x[1:])):
    w = wallets[wid]
    nook_raw = get_nook_balance(w["addr"])
    nook_fmt = nook_raw / 1e18
    total_initial += nook_fmt
    print("%-5s %12.4f NOOK" % (wid, nook_fmt))
    time.sleep(0.3)
print("Total: %.4f NOOK\n" % total_initial)

if total_initial == 0:
    print("All wallets already empty. Nothing to send.")
    sys.exit(0)

gas_price = int(get_gas_price() * 1.2)
grand_total_sent = 0

for pass_num in range(1, MAX_PASSES + 1):
    print("--- Pass %d ---" % pass_num)
    sent, total_sent = sweep_pass(wallets, gas_price, pass_num)
    grand_total_sent += total_sent
    print("Pass %d: %d transfers, %.4f NOOK" % (pass_num, sent, total_sent))

    if sent == 0:
        print("No wallets had balance. Sweep complete.")
        break

    # Brief wait for txs to confirm, then verify
    print("Waiting 3s for tx confirmation...")
    time.sleep(3)

    # Quick verify
    remaining = 0
    for wid in sorted(wallets.keys(), key=lambda x: int(x[1:])):
        w = wallets[wid]
        nook_raw = get_nook_balance(w["addr"])
        remaining += nook_raw / 1e18
        time.sleep(0.3)

    if remaining == 0:
        print("All wallets empty after pass %d. Done." % pass_num)
        break
    else:
        print("%.4f NOOK still remaining, re-sweeping..." % remaining)
        gas_price = int(get_gas_price() * 1.2)  # refresh gas price

# === FINAL VERIFICATION ===
print("\n=== FINAL VERIFICATION ===")
total_remaining = 0
all_empty = True
for wid in sorted(wallets.keys(), key=lambda x: int(x[1:])):
    w = wallets[wid]
    nook_raw = get_nook_balance(w["addr"])
    nook_fmt = nook_raw / 1e18
    total_remaining += nook_fmt
    status = "OK" if nook_raw == 0 else "FAIL"
    if nook_raw > 0:
        all_empty = False
    print("%-5s %12.4f NOOK  [%s]" % (wid, nook_fmt, status))
    time.sleep(0.3)

# Destination balance
padded = DEST[2:].lower().zfill(64)
dest_result, _ = rpc_call("eth_call", [{"to": NOOK_TOKEN, "data": "0x70a08231" + padded}, "latest"])
dest_bal = int(dest_result, 16) / 1e18 if dest_result and dest_result != "0x" else 0

print("\nTotal remaining: %.4f NOOK" % total_remaining)
print("Total sent: %.4f NOOK" % grand_total_sent)
print("Destination balance: %.4f NOOK" % dest_bal)

if all_empty:
    print("SUCCESS: All 15 wallets empty.")
else:
    print("WARNING: Some wallets still have balance after %d passes." % MAX_PASSES)
