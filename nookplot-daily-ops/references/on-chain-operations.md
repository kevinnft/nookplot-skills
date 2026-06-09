# Nookplot On-Chain Operations (Base Mainnet)

NOOK is an ERC-20 token on Base mainnet. On-chain ops are separate from the
Nookplot gateway API — they go directly to the chain.

## Key Constants

| Item | Value |
|------|-------|
| NOOK token | `0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3` |
| Chain | Base mainnet (ID 8453) |
| Public RPC | `https://mainnet.base.org` |
| Block explorer | `https://basescan.org` / `https://base.blockscout.com` |
| Reward distributor | `0x3632428A...` (on-chain sender of mining rewards) |
| Gas token | ETH on Base (~$0.001 per ERC-20 transfer) |

## Address Validation (CRITICAL)

Ethereum addresses = `0x` + 40 hex characters. Always validate BEFORE passing
to `Web3.to_checksum_address()` — it throws a confusing `ValueError: Unknown
format` if the address is even 1 char short.

```python
def validate_address(addr):
    if not addr.startswith('0x'): return False
    if len(addr) != 42: return False  # 2 (0x) + 40 (hex)
    try: int(addr[2:], 16)
    except ValueError: return False
    return True
```

## Checking NOOK Balances

### Via curl (no web3 dependency)
```bash
NOOK="0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3"
# balanceOf(address) selector = 0x70a08231
ADDR_PADDED=$(echo "YOUR_ADDRESS" | sed 's/0x//' | tr '[:upper:]' '[:lower:]' | xargs printf '%064s' | tr ' ' '0')
curl -sS -X POST https://mainnet.base.org \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"eth_call\",\"params\":[{\"to\":\"$NOOK\",\"data\":\"0x70a08231$ADDR_PADDED\"},\"latest\"]}"
# Result is hex uint256 — divide by 1e18 for NOOK
```

### Via web3.py
```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
contract = w3.eth.contract(address=Web3.to_checksum_address(NOOK), abi=ERC20_ABI)
balance = contract.functions.balanceOf(Web3.to_checksum_address(addr)).call() / 1e18
```

### Rate limits
Base public RPC rate limits aggressively. Space reads by 0.5-1s, writes by 3s.
Batch-checking all 15 wallets takes ~15s with proper spacing.

## Transferring NOOK Tokens

Use `scripts/nook_transfer.py`:
```bash
python3 ~/.hermes/skills/nookplot/nookplot-daily-ops/scripts/nook_transfer.py 0xDEST_ADDRESS
```

Or inline with web3.py (EIP-1559 type 2 tx):
```python
tx = contract.functions.transfer(
    Web3.to_checksum_address(dest), amount_wei
).build_transaction({
    'from': sender_cs, 'nonce': nonce, 'gas': 70000,
    'maxFeePerGas': base_fee + priority_fee,
    'maxPriorityFeePerGas': w3.to_wei(0.001, 'gwei'),
    'chainId': 8453, 'type': 2,
})
signed = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
```

## Private Key Locations

Each wallet's `.env` file at `~/nookplot-{name}/.env` contains:
- `NOOKPLOT_AGENT_PRIVATE_KEY=0x...` — the signing key (always present)
- `WALLET_PRIVATE_KEY=...` — same key, may or may not have 0x prefix
- `NOOKPLOT_PRIVATE_KEY=0x...` — same key (legacy name, some wallets)

Use `NOOKPLOT_AGENT_PRIVATE_KEY` as canonical source. Ensure 0x prefix.

## Pitfalls

1. **execute_code sandbox has no web3** — web3.py is installed system-wide at
   `~/.local/lib/python3.12/site-packages/web3`. The execute_code sandbox uses
   a different Python env. Use `terminal()` with a script file instead.

2. **Address length** — `to_checksum_address()` fails silently-confusingly on
   39-char addresses. Always validate length = 42 before calling.

3. **Gas check before transfer** — each wallet needs ~0.000005 ETH on Base.
   Wallets funded with only NOOK (no ETH) will fail to send. Check ETH balance
   first; if 0, fund via bridge before transferring.

4. **Rate limit spacing** — sequential transfers, 3s between each. Parallel
   sends from same IP will get rejected by Base RPC.

5. **Amount precision** — NOOK is 18 decimals. Use `int(balance * 1e18)` for
   the full balance. Don't round or you'll leave dust.

6. **Source .env breaks for kaiju8** — mnemonic has spaces. Use Python line
   parser instead of `source .env` in bash.
