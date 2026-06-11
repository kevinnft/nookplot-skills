#!/usr/bin/env python3
"""Transfer all NOOK tokens from W1-W15 wallets to a target address on Base chain.
Usage: ~/.hermes/hermes-agent/venv/bin/python scripts/transfer_all_nook.py <TARGET_ADDRESS>
Defaults to 0xb1caec6d89f2d62db3416054096070c340dc2c41 if no arg provided."""
import json, time, sys
from web3 import Web3
from eth_account import Account

# Config
TARGET_ADDR = sys.argv[1] if len(sys.argv) > 1 else "0xb1caec6d89f2d62db3416054096070c340dc2c41"
TOKEN_ADDR = "0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3"
# Use blastapi to avoid 429 rate limits from mainnet.base.org
RPC_URL = "https://base-mainnet.public.blastapi.io"
WALLETS_FILE = "/home/asus/.hermes/nookplot_wallets.json"

ERC20_ABI = json.loads('[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]')

w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={'timeout': 30}))
if not w3.is_connected():
    print("❌ Failed to connect to Base RPC")
    sys.exit(1)

TARGET_CHECKSUM = Web3.to_checksum_address(TARGET_ADDR)
TOKEN_CHECKSUM = Web3.to_checksum_address(TOKEN_ADDR)

with open(WALLETS_FILE) as f:
    wallets = json.load(f)

token = w3.eth.contract(address=TOKEN_CHECKSUM, abi=ERC20_ABI)
# Base ERC20 transfer gas is ~0.00002 ETH, so 0.00005 is safe minimum
MIN_ETH = w3.to_wei(0.00005, 'ether')

print(f"Network: Base (chainId: {w3.eth.chain_id})")
print(f"Token: {TOKEN_CHECKSUM}")
print(f"Target: {TARGET_CHECKSUM}")
print(f"Wallets: {len(wallets)}\n")

results = []
total_transferred = 0

for wid in sorted(wallets.keys(), key=lambda x: int(x[1:])):
    w = wallets[wid]
    name = w.get("displayName", wid)
    addr = w["addr"]
    pk = w.get("pk")
    
    print(f"[{wid}] {name} ({addr[:10]}...)")
    
    if not pk:
        print(f"  ⏭ SKIP: No private key")
        results.append({"wallet": wid, "name": name, "status": "no_pk", "balance": 0.0, "eth": 0.0, "tx": None})
        continue
    
    addr_checksum = Web3.to_checksum_address(addr)
    nook_balance = token.functions.balanceOf(addr_checksum).call()
    nook_balance_float = float(Web3.from_wei(nook_balance, 'ether'))
    eth_balance = w3.eth.get_balance(addr_checksum)
    eth_balance_float = float(Web3.from_wei(eth_balance, 'ether'))
    
    print(f"  NOOK: {nook_balance_float:.4f}")
    print(f"  ETH:  {eth_balance_float:.6f}")
    
    if nook_balance == 0:
        print(f"  ⏭ SKIP: No NOOK balance")
        results.append({"wallet": wid, "name": name, "status": "no_nook", "balance": 0.0, "eth": eth_balance_float, "tx": None})
        continue
    
    if eth_balance < MIN_ETH:
        print(f"  ❌ SKIP: Insufficient ETH for gas (need 0.00005 ETH)")
        results.append({"wallet": wid, "name": name, "status": "no_eth", "balance": nook_balance_float, "eth": eth_balance_float, "tx": None})
        continue
    
    nonce = w3.eth.get_transaction_count(addr_checksum)
    tx = token.functions.transfer(TARGET_CHECKSUM, nook_balance).build_transaction({
        'chainId': 8453, 'gas': 100000, 'gasPrice': w3.eth.gas_price, 'nonce': nonce
    })
    
    signed = Account.sign_transaction(tx, pk)
    
    try:
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        tx_hash_hex = '0x' + tx_hash.hex()
        print(f"  ✅ Sent: {nook_balance_float:.4f} NOOK | TX: {tx_hash_hex}")
        results.append({"wallet": wid, "name": name, "status": "success", "balance": nook_balance_float, "eth": eth_balance_float, "tx": tx_hash_hex})
        total_transferred += nook_balance_float
    except Exception as e:
        print(f"  ❌ TX failed: {e}")
        results.append({"wallet": wid, "name": name, "status": "tx_fail", "balance": nook_balance_float, "eth": eth_balance_float, "tx": None, "error": str(e)})
    
    time.sleep(3)  # Avoid 429 rate limits

print(f"\n{'='*60}")
print("VERIFICATION - Final NOOK balances")
print(f"{'='*60}")
remaining = 0
for r in results:
    if r["status"] == "success":
        w = wallets[r["wallet"]]
        addr_checksum = Web3.to_checksum_address(w["addr"])
        final_balance = token.functions.balanceOf(addr_checksum).call()
        final_balance_float = float(Web3.from_wei(final_balance, 'ether'))
        remaining += final_balance_float
        status = "✅ 0.0000" if final_balance == 0 else f"⚠️ {final_balance_float:.4f} remaining"
        print(f"  {r['wallet']} ({r['name']}): {status}")

print(f"\n{'='*60}\nSUMMARY\n{'='*60}")
success = [r for r in results if r["status"] == "success"]
skipped = [r for r in results if r["status"] != "success"]
print(f"✅ Transferred: {len(success)} wallets")
print(f"⏭ Skipped: {len(skipped)} wallets")
print(f"Total NOOK sent: {total_transferred:,.4f}")
print(f"Remaining in wallets: {remaining:,.4f}\n")

for r in success:
    print(f"  {r['wallet']} ({r['name']}): {r['balance']:,.4f} NOOK | tx: {r['tx']}")
for r in skipped:
    print(f"  {r['wallet']} ({r['name']}): {r['status']} (NOOK: {r['balance']:,.4f}, ETH: {r['eth']:.6f})")
# Save results
import decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super().default(o)

with open("/tmp/transfer_nook_results.json", "w") as f:
    json.dump(results, f, indent=2, cls=DecimalEncoder)
print(f"\nSaved to /tmp/transfer_nook_results.json")
