---
name: nookplot-token-transfer
description: Transfer all NOOK tokens from W1-W15 wallets to a target address on Base chain. Use when user asks to send/transfer NOOK balances.
---

# NOOK Token Transfer

## Quick Facts
- **Network**: Base (chainId: 8453)
- **RPC**: `https://base-mainnet.public.blastapi.io` (mainnet.base.org 429s aggressively)
- **Token**: `0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3`
- **Wallets**: `/home/asus/.hermes/nookplot_wallets.json` (W1-W15, each has `pk` + `addr`)
- **Python**: `/home/asus/.hermes/hermes-agent/venv/bin/python` (web3.py installed)

## Pitfalls (Learned Jun 8-10, 2026)
1. **Checksum addresses REQUIRED** — web3.py rejects lowercase. Use `Web3.to_checksum_address(addr)` for ALL addresses (token, dest, sender).
2. **`signed.raw_transaction`** — NOT `signed.rawTransaction` (deprecated, throws AttributeError in newer web3.py).
3. **RPC rate limit (429)** — Base mainnet `mainnet.base.org` rate-limits aggressively after ~9 wallets. Use `https://base-mainnet.public.blastapi.io` as PRIMARY RPC (confirmed working for 15 wallets sequential with 2s sleep, Jun 10).
4. **Gas check** — Each wallet needs ~0.00005 ETH for gas (NOT 0.0001). Check `w3.eth.get_balance()` before building tx. Skip wallets with insufficient ETH.
5. **Transfer full balance** — Use `token.functions.balanceOf(addr).call()` to get exact balance, send entire amount.
6. **Gas params** — `gas: 100000`, `gasPrice: w3.eth.gas_price` works reliably for ERC20 transfer on Base.
7. **web3 v7.x has NO `geth_poa_middleware`** — `from web3.middleware import geth_poa_middleware` throws ImportError on web3 7.16.0. Simply remove it — Base chain doesn't need PoA middleware injection.
8. **Sleep 2s between tx sends** — Prevents RPC 429. Sleep 3s before final balance verification pass.
9. **Decimal serialization** — `Web3.from_wei()` returns Decimal objects. When saving results to JSON, convert with `float()` or use custom encoder.
7. **web3.py 7.x: no geth_poa_middleware** — `from web3.middleware import geth_poa_middleware` fails in v7.16.0. Just remove it; Base works without PoA middleware in web3 v7.
8. **Decimal not JSON serializable** — `Web3.from_wei()` returns `Decimal` objects. Use `float()` when building JSON results dicts.

## Procedure
1. Read wallets JSON
2. Use `https://base-mainnet.public.blastapi.io` as RPC (NOT mainnet.base.org — 429s)
3. For each wallet: check balance → check ETH for gas (MIN 0.00005 ETH) → build tx → sign → send → sleep 3s
4. After all transfers: sleep 3s → verify all balances are 0
5. Report: table of wallet → amount → tx hash, then final balance confirmation
6. Convert `Web3.from_wei()` results with `float()` before JSON serialization

## Script Location
Reusable script: `scripts/transfer_all_to_target.py`
Usage: `python scripts/transfer_all_to_target.py <target_address>`
Requires: web3.py, eth_account in hermes venv. Wallets at `~/.hermes/nookplot_wallets.json`.
Usage: Edit `TARGET_ADDR` at the top, then run:
```bash
~/.hermes/hermes-agent/venv/bin/python ~/.hermes/skills/nookplot/nookplot-token-transfer/scripts/transfer_all_nook.py
```
