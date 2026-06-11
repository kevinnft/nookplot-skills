---
name: nookplot-nook-transfer
description: "Check and transfer NOOK ERC-20 balances from all 15 wallets on Base network. Quick reference for token contract, RPC calls, and batch transfer."
tags: [nookplot, nook, erc20, transfer, base-network]
version: 1
---

# Nookplot NOOK Token Transfer

## Token Info
- **NOOK Token Contract (Base):** `0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3`
- **Decimals:** 18
- **Total Supply:** 100,000,000,000 NOOK
- **Chain:** Base (chainId 8453)
- **RPC:** `https://mainnet.base.org`

## Related Contracts
| Contract | Address |
|----------|---------|
| NOOK Token | `0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3` |
| Credit Packs | `0x1A8C121e5C79623986f85F74C66d9cAd086B2358` |
| Mining Forwarder | `0x3632428A9878D2B58f58F9Ef7C57Cb0eE5760A01` |
| EIP-712 Forwarder | `0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80` |

> Token address discovered via `GET /v1/credits/packs` endpoint — returns `nookTokenAddress` field.

## Check Balances (All 15 Wallets)

```bash
# Use Hermes venv Python (has eth_account)
~/.hermes/hermes-agent/venv/bin/python
```

```python
import json, subprocess, time

wallets = json.loads(open("/home/asus/.hermes/nookplot_wallets.json").read())
BASE_RPC = "https://mainnet.base.org"
NOOK_TOKEN="0xb2...def eth_call(to, data, retries=3):
    payload = json.dumps({"jsonrpc":"2.0","method":"eth_call",
        "params":[{"to":to,"data":data},"latest"],"id":1})
    for a in range(retries):
        r = subprocess.run(["curl","-s","--max-time","10","-X","POST",
            BASE_RPC,"-H","Content-Type: application/json","-d",payload],
            capture_output=True, text=True, timeout=15)
        try:
            val = json.loads(r.stdout).get("result")
            if val and val != "0x": return val
        except: pass
        time.sleep(1)
    return "0x0"

for wid in sorted(wallets.keys(), key=lambda x: int(x[1:])):
    w = wallets[wid]
    addr = w["addr"]
    padded = addr[2:].lower().zfill(64)
    nh = eth_call(NOOK_TOKEN, "0x70a08231" + padded)
    nb = int(nh, 16) / 1e18 if nh and nh != "0x" else 0
    print("%-6s %-12s %s NOOK" % (wid, w.get("displayName","")[:12], f"{nb:,.4f}"))
    time.sleep(0.5)  # CRITICAL: pace RPC calls
```

## Transfer All NOOK to Destination

```python
import json, subprocess, time
from eth_account import Account

BASE_RPC = "https://mainnet.base.org"
NOOK_TOKEN="0xb2...DEST = "0x..."  # destination address
CHAIN_ID = 8453
wallets = json.loads(open("/home/asus/.hermes/nookplot_wallets.json").read())

def rpc_call(method, params=None):
    payload = json.dumps({"jsonrpc":"2.0","method":method,"params":params or [],"id":1})
    r = subprocess.run(["curl","-s","--max-time","15","-X","POST",BASE_RPC,
        "-H","Content-Type: application/json","-d",payload],
        capture_output=True, text=True, timeout=20)
    resp = json.loads(r.stdout)
    if "error" in resp: return None, resp["error"]
    return resp.get("result"), None

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

# Main loop
gas_price = int(get_gas_price() * 1.2)  # 20% buffer

for wid in sorted(wallets.keys(), key=lambda x: int(x[1:])):
    w = wallets[wid]
    addr = w["addr"]; pk = w["pk"]
    nook_raw = get_nook_balance(addr)
    if nook_raw == 0:
        print("%s SKIP (0 NOOK)" % wid); continue
    
    nonce = get_nonce(addr)
    calldata = build_transfer_calldata(DEST, nook_raw)
    tx = {"to": NOOK_TOKEN, "value": 0, "gas": 100000,
          "gasPrice": gas_price, "nonce": nonce,
          "data": calldata, "chainId": CHAIN_ID}
    
    account = Account.from_key(pk)
    signed = account.sign_transaction(tx)
    raw_tx = "0x" + signed.raw_transaction.hex()
    
    tx_hash, err = rpc_call("eth_sendRawTransaction", [raw_tx])
    if err:
        print("%s ERROR: %s" % (wid, err))
    else:
        print("%s SENT %s NOOK -> %s" % (wid, f'{nook_raw/1e18:,.4f}', tx_hash))
    
    time.sleep(1)  # CRITICAL: pace between wallets
```

## Verify Transfers

```python
# Check destination balance after transfer
def rpc(method, params):
    p = json.dumps({"jsonrpc":"2.0","method":method,"params":params,"id":1})
    r = subprocess.run(["curl","-s","--max-time","15","-X","POST",BASE_RPC,
        "-H","Content-Type: application/json","-d",p],
        capture_output=True, text=True, timeout=20)
    return json.loads(r.stdout).get("result","0x0")

padded = DEST[2:].lower().zfill(64)
bal_hex = rpc("eth_call", [{"to": NOOK_TOKEN, "data": "0x70a08231" + padded}, "latest"])
bal = int(bal_hex, 16) / 1e18
print("Destination balance: %s NOOK" % f"{bal:,.4f}")

# Check tx receipt status
receipt = rpc("eth_getTransactionReceipt", [tx_hash])
status = receipt.get("status")  # "0x1" = success, "0x0" = revert
```

## Pitfalls

1. **Multi-Pass Sweep Required (CRITICAL)**: Wallets can receive new rewards (mining payouts, airdrops, etc.) *during* or immediately after a transfer sweep. A single-pass transfer is often insufficient to "send all balances". Always run a final verification pass after the initial sweep. If any wallet shows >0 balance, perform a secondary sweep until all 15 wallets read exactly 0 NOOK. **Confirmed working Jun 9**: Pass 1 swept 14 wallets, W1 received new rewards during transfer, Pass 2 swept W1 (47,489 NOOK). All 15 wallets verified empty after 2 passes. Total: 484,172 NOOK transferred in 15 txs.

2. **RPC Rate Limits**: Base public RPC (`mainnet.base.org`) rate-limits aggressively. MUST use `time.sleep(0.5)` between balance checks and `time.sleep(1)` to `time.sleep(2)` between send transactions. Without pacing, wallets randomly return 0 balances or 429 errors.

3. **Gas Cost Calculation**: ~37K-54K gas per ERC-20 transfer. At 0.006 gwei (Base L2), cost is ~0.0000004 ETH per tx. Wallets hold ~0.0001 ETH each — more than enough for multiple transfers. **CRITICAL**: Always calculate exact gas cost (`gas_cost = gas_price * gas_limit`) and check `eth_bal < gas_cost`. Do NOT hardcode a minimum ETH balance check (e.g., `0.0001 ETH`), as it can falsely skip wallets that have sufficient gas.

4. **web3.py Checksum Addresses**: `web3.py` strictly enforces EIP-55 checksum addresses. Passing lowercase addresses will throw: `'web3.py only accepts checksum addresses...'`. **FIX**: Always wrap ALL addresses with `Web3.to_checksum_address(addr)` before passing to web3.py methods (balance checks, transfers, destination).

5. **Signed Transaction Attribute**: When using `web3.py`'s `account.sign_transaction(tx)`, the resulting object uses `raw_transaction` (lowercase with underscore), NOT `rawTransaction`. Using the wrong attribute throws: `'SignedTransaction' object has no attribute 'rawTransaction'`.

6. **eth_account Import**: System Python doesn't allow pip install. Use `~/.hermes/hermes-agent/venv/bin/python` which has web3/eth_account pre-installed.

7. **PK Required**: All wallets need private key in `wallets.json` (`pk` field). Without PK, cannot sign raw tx. Use EIP-712 relay via gateway instead.

8. **balanceOf selector**: `0x70a08231` — standard ERC-20 balanceOf(address). Address MUST be 0-padded to 64 chars.

9. **transfer selector**: `0xa9059cbb` — standard ERC-20 transfer(address,uint256). Both params 0-padded to 64 chars.

10. **Verify After Send**: Always check destination balance AND tx receipt status=0x1 to confirm success.

## Quick Commands

```bash
# Full multi-pass sweep (recommended - handles reward re-entrancy)
~/.hermes/hermes-agent/venv/bin/python ~/.hermes/skills/nookplot/nookplot-nook-transfer/scripts/sweep_all.py <DEST_ADDRESS>
```

# Check destination balance inline
~/.hermes/hermes-agent/venv/bin/python -c "
import json, subprocess
BASE_RPC='https://mainnet.base.org'
NT='0xb2...='0xb1caec6d89f2d62db3416054096070c340dc2c41'
p=DEST[2:].lower().zfill(64)
r=subprocess.run(['curl','-s','-X','POST',BASE_RPC,'-H','Content-Type: application/json','-d',json.dumps({'jsonrpc':'2.0','method':'eth_call','params':[{'to':NT,'data':'0x70a08231'+p},'latest'],'id':1})],capture_output=True,text=True,timeout=15)
bal=int(json.loads(r.stdout)['result'],16)/1e18
print('NOOK: %s' % f'{bal:,.4f}')
"
```
