#!/usr/bin/env python3
"""
Batch transfer NOOK ERC-20 tokens from all wallets to a destination address.
Run via: python3 ~/.hermes/skills/nookplot/nookplot-daily-ops/scripts/nook_transfer.py <DEST_ADDRESS>

Requirements: web3 (pip3 install web3 --user)
Chain: Base mainnet (8453)
"""
import json, os, sys, time
from web3 import Web3

NOOK = "0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3"
RPC = "https://mainnet.base.org"
CHAIN_ID = 8453
HOME = "/home/ryzen"

ERC20_ABI = json.loads('''[
  {"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf",
   "outputs":[{"name":"balance","type":"uint256"}],"type":"function"},
  {"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],
   "name":"transfer","outputs":[{"name":"","type":"bool"}],"type":"function"}
]''')

WALLETS = [
    'abel', 'bagong', 'ball', 'din', 'don', 'gord', 'gordon',
    'heist', 'herdnol', 'jordi', 'kaiju8', 'kikuk', 'kimak', 'liau', 'pratama'
]

def get_pk(name):
    """Extract NOOKPLOT_AGENT_PRIVATE_KEY from wallet .env"""
    env_path = f"{HOME}/nookplot-{name}/.env"
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith('NOOKPLOT_AGENT_PRIVATE_KEY='):
                val = line.split('=', 1)[1].strip()
                if not val.startswith('0x'):
                    val = '0x' + val
                return val
    return None

def get_address(name):
    """Extract wallet address from .env"""
    env_path = f"{HOME}/nookplot-{name}/.env"
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if 'ADDRESS' in line and '=' in line:
                val = line.split('=', 1)[1].strip()
                if val.startswith('0x') and len(val) == 42:
                    return val
    return None

def validate_address(addr):
    """Validate Ethereum address format — must be 42 chars (0x + 40 hex)."""
    if not addr or not addr.startswith('0x'):
        return False, "missing 0x prefix"
    hex_part = addr[2:]
    if len(hex_part) != 40:
        return False, f"wrong length: {len(hex_part)} hex chars (need 40)"
    try:
        int(hex_part, 16)
    except ValueError:
        return False, "contains non-hex characters"
    return True, "ok"

def check_balances(w3, contract):
    """Check NOOK + ETH balances for all wallets."""
    results = []
    for name in WALLETS:
        addr = get_address(name)
        if not addr:
            results.append((name, None, None, None, 'no address in .env'))
            continue
        cs = Web3.to_checksum_address(addr)
        try:
            nook = contract.functions.balanceOf(cs).call() / 1e18
            eth = w3.from_wei(w3.eth.get_balance(cs), 'ether')
            results.append((name, addr, nook, float(eth), ''))
        except Exception as e:
            results.append((name, addr, None, None, str(e)))
        time.sleep(0.5)  # rate limit spacing for reads
    return results

def transfer_nook(w3, contract, dest, wallet_name, amount_wei, pk):
    """Send NOOK tokens from one wallet."""
    addr = get_address(wallet_name)
    cs_addr = Web3.to_checksum_address(addr)
    nonce = w3.eth.get_transaction_count(cs_addr)

    base_fee = w3.eth.get_block('latest').get('baseFeePerGas', w3.to_wei(0.001, 'gwei'))
    max_pri = w3.to_wei(0.001, 'gwei')
    max_fee = base_fee + max_pri

    tx = contract.functions.transfer(
        Web3.to_checksum_address(dest), amount_wei
    ).build_transaction({
        'from': cs_addr, 'nonce': nonce, 'gas': 70000,
        'maxFeePerGas': max_fee, 'maxPriorityFeePerGas': max_pri,
        'chainId': CHAIN_ID, 'type': 2,
    })

    signed = w3.eth.account.sign_transaction(tx, pk)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return tx_hash.hex()

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 nook_transfer.py <DESTINATION_ADDRESS>")
        print("  Checks all wallet balances and transfers NOOK to destination.")
        sys.exit(1)

    dest = sys.argv[1]
    valid, msg = validate_address(dest)
    if not valid:
        print(f"ERROR: Invalid destination address '{dest}' — {msg}")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(RPC))
    contract = w3.eth.contract(address=Web3.to_checksum_address(NOOK), abi=ERC20_ABI)

    print("=" * 70)
    print("NOOK Balance Check — Base Mainnet")
    print("=" * 70)
    print(f"{'Wallet':<10} {'Address':<44} {'NOOK':>15} {'ETH':>12}")
    print("-" * 85)

    balances = check_balances(w3, contract)
    total = 0
    send_list = []

    for name, addr, nook, eth, err in balances:
        if err:
            print(f"{name:<10} {addr or 'N/A':<44} {'ERR':>15} {'':>12}  [{err}]")
            continue
        nook_str = f"{nook:,.4f}" if nook is not None else "ERR"
        eth_str = f"{eth:.6f}" if eth is not None else "ERR"
        marker = " <-- HAS NOOK" if (nook and nook > 0) else ""
        print(f"{name:<10} {addr:<44} {nook_str:>15} {eth_str:>12}{marker}")
        if nook and nook > 0:
            total += nook
            send_list.append((name, addr, nook))

    print("-" * 85)
    print(f"{'TOTAL':<10} {'':<44} {total:>15,.4f}")
    print(f"\nDestination: {dest}")
    print(f"Wallets with NOOK: {len(send_list)}")

    if not send_list:
        print("\nNothing to transfer.")
        return

    confirm = input(f"\nTransfer {total:,.4f} NOOK from {len(send_list)} wallets? [y/N]: ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return

    print("\nExecuting transfers...")
    for name, addr, nook in send_list:
        pk = get_pk(name)
        if not pk:
            print(f"[{name}] SKIP — no private key")
            continue

        amount_wei = int(nook * 1e18)
        try:
            tx_hex = transfer_nook(w3, contract, dest, name, amount_wei, pk)
            print(f"[{name}] SENT {nook:,.4f} NOOK | tx: 0x{tx_hex}")
        except Exception as e:
            print(f"[{name}] FAILED: {e}")

        time.sleep(3)  # spacing between writes

    print("\nDone. Verify on https://basescan.org")

if __name__ == '__main__':
    main()
