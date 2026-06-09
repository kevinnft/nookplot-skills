# curl-Based RPC Approach for Base Network

When `web3.py` consistently hits 403 Forbidden or 429 rate limits on `https://mainnet.base.org`, use `curl` via `subprocess` instead. This approach is more reliable because:
- curl includes proper headers by default
- You can control retry logic explicitly
- Works from both `terminal()` and script files

## RPC Helper Function

```python
import json, subprocess, time

RPC = "https://mainnet.base.org"

def rpc(method, params, retries=3):
    """Call Base RPC via curl with retry logic for rate limits."""
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1})
    for attempt in range(retries):
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", RPC,
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True, text=True, timeout=30
        )
        r = json.loads(result.stdout)
        if "error" in r:
            if "rate limit" in r["error"].get("message", "").lower() and attempt < retries - 1:
                time.sleep(2)
                continue
            raise Exception(f"RPC error: {r['error']}")
        return r["result"]
    raise Exception("RPC rate limit exceeded after retries")
```

## Balance Check

```python
NOOK_TOKEN="0xb2..._SIG = "0x70a08231"

def get_nook_balance(addr):
    padded = "0x" + ERC20_BALANCEOF_SIG[2:] + "0" * 24 + addr[2:].lower()
    result = rpc("eth_call", [{"to": NOOK_TOKEN, "data": padded}, "latest"])
    return int(result, 16) / 1e18

def get_eth_balance(addr):
    return int(rpc("eth_getBalance", [addr, "latest"]), 16) / 1e18
```

## ERC-20 Transfer via curl

```python
from eth_account import Account

ERC20_TRANSFER_SIG = "0xa9059cbb"

def build_transfer_tx(from_addr, to_addr, amount, nonce, gas_price, private_key):
    """Build and sign ERC-20 transfer transaction."""
    to_padded = "0" * 24 + to_addr[2:].lower()
    amount_hex = hex(amount)[2:].zfill(64)
    data = ERC20_TRANSFER_SIG + to_padded + amount_hex
    
    tx = {
        "from": from_addr,
        "to": NOOK_TOKEN,
        "data": data,
        "value": "0x0",
        "nonce": hex(nonce),
        "gasPrice": hex(gas_price),
        "chainId": 8453
    }
    
    try:
        gas_est = int(rpc("eth_estimateGas", [tx]), 16)
        tx["gas"] = hex(int(gas_est * 1.2))
    except Exception as e:
        print(f"    Gas estimate failed ({e}), using 100000")
        tx["gas"] = hex(100000)
    
    signed = Account.sign_transaction(tx, private_key)
    return signed

def send_raw(raw_hex):
    return rpc("eth_sendRawTransaction", [raw_hex])

def wait_receipt(tx_hash, timeout=120):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = rpc("eth_getTransactionReceipt", [tx_hash])
            if r is not None:
                return r
        except:
            pass
        time.sleep(3)
    return None
```

## Full Transfer Example

```python
def transfer_nook(from_addr, private_key, to_addr, amount_raw):
    nonce = int(rpc("eth_getTransactionCount", [from_addr, "latest"]), 16)
    gas_price = int(rpc("eth_gasPrice", []), 16)
    time.sleep(0.3)
    
    signed = build_transfer_tx(from_addr, to_addr, amount_raw, nonce, gas_price, private_key)
    
    raw_hex = signed.raw_transaction.hex()
    if not raw_hex.startswith("0x"):
        raw_hex = "0x" + raw_hex
    
    tx_hash = send_raw(raw_hex)
    receipt = wait_receipt(tx_hash)
    return receipt and receipt.get("status") == "0x1"
```

## Rate Limiting

Base public RPC rate-limits aggressively. Best practices:
- Space calls by 0.3-1s for balance checks
- Space calls by 1-2s for transaction submission
- Add exponential backoff on 429: `time.sleep(2 ** attempt)`
- For bulk operations (15 wallets), expect 2-3 rate limit hits that need retry
