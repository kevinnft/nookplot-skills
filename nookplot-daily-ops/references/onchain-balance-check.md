# On-Chain Balance Check — Base Mainnet Direct RPC

Direct NOOK ERC-20 balance check via Base mainnet RPC. No CLI or API needed.

## Constants

```
NOOK Token: 0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3
RPC:        https://mainnet.base.org
Chain:      Base mainnet (8453)
```

## Balance Check Function

```python
import subprocess, json

NOOK = "0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3"
RPC = "https://mainnet.base.org"

def nook_balance(addr):
    """Check NOOK ERC-20 balance for address on Base mainnet."""
    data = "0x70a08231" + addr.lower().replace("0x", "").zfill(64)
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "eth_call",
        "params": [{"to": NOOK, "data": data}, "latest"]
    })
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "15", "-X", "POST", RPC,
         "-H", "Content-Type: application/json", "-d", payload],
        capture_output=True, text=True, timeout=20)
    try:
        resp = json.loads(r.stdout)
        return int(resp["result"], 16) / 1e18
    except:
        return 0

def eth_balance(addr):
    """Check native ETH balance on Base mainnet."""
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "eth_getBalance",
        "params": [addr, "latest"]
    })
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "15", "-X", "POST", RPC,
         "-H", "Content-Type: application/json", "-d", payload],
        capture_output=True, text=True, timeout=20)
    try:
        resp = json.loads(r.stdout)
        return int(resp.get("result", "0x0"), 16) / 1e18
    except:
        return 0
```

## Usage

```python
# Check single wallet
nook = nook_balance("0xF98981a94271195703a0377aab9B1Cfdc5d8839b")
print(f"NOOK: {nook:,.2f}")

# Check all fleet wallets (with 2s spacing for rate limits)
for w in WALLETS:
    addr = get_address(w)
    nook = nook_balance(addr)
    time.sleep(2)
    eth = eth_balance(addr)
    time.sleep(2)
    print(f"{w}: {nook:,.2f} NOOK, {eth:.6f} ETH")
```

## Rate Limits

Base public RPC (`mainnet.base.org`) rate limits aggressively:
- Use `time.sleep(2)` between calls minimum
- Retry on empty/error results
- ~30 calls per minute sustainable

## Pitfalls

1. **Claim vs on-chain timing** — After `nookplot_claim_mining_reward`, wait 2-4 seconds for on-chain settlement before checking balance
2. **Address case sensitivity** — Always `.lower()` the address for `balanceOf` data encoding
3. **Result parsing** — `int(result, 16)` converts hex string to int. Handle `"0x0"` gracefully.
4. **Different from API balance** — API `totalEarned` includes pending/unfinalized rewards. On-chain balance only shows actually claimed+settled tokens.

## Verified June 2, 2026

All 15 wallets checked via this method. Post-claim results:
- don: 269,912 NOOK (largest — guild inference from treasury deposits)
- herdnol: 25,317 NOOK
- gordon: 21,085 NOOK
- heist: 19,400 NOOK
- din: 18,757 NOOK
- abel: 18,636 NOOK
- jordi: 18,021 NOOK
- ball: 17,715 NOOK
- bagong/gord/kimak: 16,029 NOOK each
- kaiju8: 9,056 NOOK
- kikuk/pratama: 5,056 NOOK each
- liau: 3,371 NOOK
- Total on-chain: 479,468 NOOK
