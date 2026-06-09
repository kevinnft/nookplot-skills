#!/usr/bin/env python3
"""Generate N Nookplot wallets with mnemonic + address + private key.
Usage: /tmp/eth_venv/bin/python3 generate-wallets.py --names bagong herdnol gordon
Requires: pip install mnemonic eth-account (in venv, not system)
"""
import argparse, json, sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--names", nargs="+", required=True, help="Wallet names")
    args = parser.parse_args()

    from mnemonic import Mnemonic
    from eth_account import Account
    Account.enable_unaudited_hdwallet_features()

    wallets = {}
    for name in args.names:
        m = Mnemonic("english")
        phrase = m.generate(strength=128)
        acct = Account.from_mnemonic(phrase)
        wallets[name] = {
            "mnemonic": phrase,
            "address": acct.address,
            "private_key": acct.key.hex()
        }
        print(f"{name}: {acct.address}", file=sys.stderr)

    print(json.dumps(wallets, indent=2))

if __name__ == "__main__":
    main()
