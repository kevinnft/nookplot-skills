# NOOK Token Contract & Balance Checking (June 2026)

## Contract Address

- **NOOK token**: `0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3` (Base chain, 18 decimals)
- **Credit packs contract**: `0x1A8C121e5C79623986f85F74C66d9cAd086B2358`
- **Mining contract**: `0x3632428A9878D2B58f58F9Ef7C57Cb0eE5760A01`
- **Forwarder contract**: `0xBAEa9E1b5222Ab79D7b194de95ff904D7E8eCf80` (NookplotForwarder, v1)

**Discovery method**: `GET /v1/credits/packs` returns `{"nookTokenAddress": "0xb233..."}` along with pack pricing.

## Three Different "Balance" Concepts

| Endpoint / Method | What It Shows | Typical Value |
|---|---|---|
| `GET /v1/revenue/balance` | claimableTokens/claimableEth from revenue distribution | Usually 0 for all wallets |
| `GET /v1/credits/balance` | Internal credit balance (for API/inference) | 700-870 credits per wallet |
| Direct RPC `eth_call` on Base | Actual NOOK ERC-20 tokens in wallet | 0-48K per wallet |

**Pitfall**: `/v1/revenue/balance` claimableTokens is NOT the same as on-chain NOOK balance. Revenue distribution is a separate mechanism from mining rewards. All wallets show 0 revenue claimable even when they hold NOOK on-chain.

## Checking On-Chain NOOK Balance (Script Pattern)

```python
import json, subprocess

NOOK_TOKEN = "0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3"
BASE_RPC = "https://mainnet.base.org"

def check_nook_balance(wallet_addr):
    # ERC-20 balanceOf(address) = 0x70a08231 + padded address
    padded = wallet_addr[2:].lower().zfill(64)
    calldata = "0x70a08231" + padded
    payload = json.dumps({
        "jsonrpc": "2.0", "method": "eth_call",
        "params": [{"to": NOOK_TOKEN, "data": calldata}, "latest"], "id": 1
    })
    cmd = ["curl", "-s", "-X", "POST", BASE_RPC, "-H", "Content-Type: application/json", "-d", payload]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    resp = json.loads(result.stdout)
    raw = int(resp.get("result", "0x0"), 16)
    return raw / 1e18  # 18 decimals

def check_eth_balance(wallet_addr):
    payload = json.dumps({"jsonrpc":"2.0","method":"eth_getBalance","params":[wallet_addr,"latest"],"id":1})
    cmd = ["curl", "-s", "-X", "POST", BASE_RPC, "-H", "Content-Type: application/json", "-d", payload]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    resp = json.loads(result.stdout)
    return int(resp.get("result", "0x0"), 16) / 1e18
```

## Cluster Balance Snapshot (June 2, 2026)

| Wallet | Name | NOOK | ETH (Base) |
|--------|------|------|------------|
| W1 | hermes | 17,300.65 | 0.00009 |
| W2 | 9dragon | 23,059.84 | 0.00007 |
| W3 | kevinft | 0 | 0.00009 |
| W4 | aboylabs | 0 | 0.00010 |
| W5 | reborn | 0 | 0.00009 |
| W6 | satoshi | 0 | 0.00009 |
| W7 | badboys | 0 | 0.00009 |
| W8 | rebirth | 0 | 0.00009 |
| W9 | john | 0 | 0.00009 |
| W10 | joni | 27,787.00 | 0.00009 |
| W11 | WhiteAgent | 48,251.39 | 0.00010 |
| W12 | PanuMan | 41,909.00 | 0.00010 |
| W13 | hemi | 9,737.00 | 0.00010 |
| W14 | kicau | 37,728.39 | 0.00010 |
| W15 | lucky | 0 | 0.00010 |
| **TOTAL** | | **205,773.27** | **0.00140** |

## Key Observations

1. Only 7 wallets hold NOOK on-chain (W1, W2, W10-W14). W3-W9 and W15 are at zero.
2. Mining proofs exist for all wallets (cumulativeAmountRaw > 0) but this is merkle allocation, not current balance.
3. The merkle rewards were claimed in prior sessions (May 25) — the NOOK was distributed but may have been spent or transferred.
4. ETH on Base is minimal (~0.001 total) — barely enough for a few transactions.
5. Basescan API is deprecated (V1) and V2 requires paid plan for Base chain. Use direct RPC.
