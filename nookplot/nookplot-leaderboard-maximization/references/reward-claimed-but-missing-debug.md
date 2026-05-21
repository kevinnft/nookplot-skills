# "Reward Sudah Diclaim Tapi Gak Masuk Wallet" — Forensic Debug Recipe

When user complains "udah claim manual tapi reward W4/W5/W6 gak masuk wallet", the
default assumption MUST be "the reward arrived and was swept", NOT "claim failed".
Reasons claim itself rarely fails silently:

- `nookplot_claim_mining_reward` (and its `/v1/actions/execute` POST equivalent)
  emits the on-chain transfer atomically with the merkle proof reveal — if it
  succeeds gateway-side, the ERC-20 transfer is in the same tx.
- `claimableBalance` going from `>0` to `0` confirms gateway accounting moved
  the reward; the question is only "where on-chain did it land".

## Step 1 — Verify on-chain DIRECTLY (bypass dashboard cache)

Dashboard, `nookplot_check_token_balance`, and even the gateway's own
`check_mining_rewards` can lag. Hit Base mainnet RPC directly:

```python
import json, subprocess
NOOK = "0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3"  # Base mainnet NOOK ERC-20

def nook_balance(addr: str) -> float:
    # ERC20 balanceOf(address) selector = 0x70a08231
    data = "0x70a08231" + addr.lower().replace("0x","").zfill(64)
    payload = json.dumps({
        "jsonrpc":"2.0","id":1,"method":"eth_call",
        "params":[{"to": NOOK, "data": data}, "latest"]
    })
    r = subprocess.run(
        ["curl","-sS","-X","POST","https://mainnet.base.org",
         "-H","Content-Type: application/json","-d",payload],
        capture_output=True, text=True, timeout=15)
    return int(json.loads(r.stdout)['result'], 16) / 1e18
```

If `nook_balance(addr) > 0` already, the claim worked. The complaint is a
viewing/cache problem, not a payment problem.

## Step 2 — Pull the actual transfer history (blockscout, no API key)

```
GET https://base.blockscout.com/api/v2/addresses/{addr}/token-transfers?type=ERC-20&token=0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3
```

Returns 50 most recent NOOK transfers with `from`, `to`, `total.value`,
`timestamp`, `transaction_hash`. Look for the most recent `IN` from the
Nookplot reward distributor `0x3632428A...` — that's the claim landing tx.
If you see one within the last hour, the claim succeeded.

## Step 3 — `totalEarned` is LIFETIME, not current balance

Critical clarification to give the user:

| Field                            | Meaning                                                   |
|----------------------------------|-----------------------------------------------------------|
| `totalEarned` (gateway)          | Lifetime cumulative NOOK ever credited to this wallet.    |
| on-chain `balanceOf` (Base)      | Current wallet balance right now.                         |
| `claimableBalance.{epoch_*}`     | Already-finalized epochs not yet swept by claim call.     |
| `pendingRewards`                 | Submissions not yet finalized (still in 24h verify queue).|

`totalEarned − on-chain balance` does NOT mean "missing rewards". It means
"reward was received and then transferred out". If `claimableBalance` is all
zeros AND on-chain shows recent IN transfers from `0x3632428A`, ALL claims
have settled. Any difference is sweep activity, not unclaimed reward.

## Step 4 — Trace OUT transfers to identify sinks

If the user genuinely doesn't see funds, inspect outflows:

```python
def out_destinations(addr: str) -> dict[str, float]:
    txs = blockscout_transfers(addr)  # see step 2
    sinks = {}
    for tx in txs:
        if tx['to']['hash'].lower() != addr.lower():  # OUT tx
            sink = tx['to']['hash']
            val = float(tx['total']['value']) / 1e18
            sinks[sink] = sinks.get(sink, 0) + val
    return sinks
```

Then classify each sink. Use the blockscout address-metadata endpoint:

```
GET https://base.blockscout.com/api/v2/addresses/{sink_addr}
```

Look at `is_contract`, `name`, `implementation_name`. Known sink classes:

### Known Base sink fingerprints (cross-cluster, May 2026)

| Address                                       | Class            | Meaning for our cluster                                                     |
|-----------------------------------------------|------------------|-----------------------------------------------------------------------------|
| `0x498581fF718922c3f8e6A244956aF099B2652b2b`  | Uniswap V4 PoolManager | NOOK → ETH/USDC swap. Reward was SOLD, not held.                      |
| `0xB1caec6D89f2d62DB3416054096070c340DC2c41`  | Consolidator EOA | Aggregates from multiple wallets in the cluster, then forwards to `0xFd78bA0F...`. Likely user-controlled but verify. |
| `0xFd78bA0F717223bEbE555A777b70b86667837ff6`  | Final sink EOA   | Terminal destination of consolidated NOOK. Usually treasury / cold wallet.  |
| `0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3`  | NOOK token contract | NOT a sink — this is the ERC-20 itself.                                  |

If outflows go to `0x498581fF` (PoolManager), that's a sale via Uniswap V4 —
look for matching ETH/USDC IN tx in the same transaction hash to see what was
received.

## Step 5 — Privkey-leak red flag

If the user denies sweeping and we see OUT transfers to addresses they don't
recognize, treat it as a potential privkey leak:

1. Stop using the wallet for new rewards.
2. Ask the user "do you control `0xB1caec6D...` (or whichever sink)?"
3. If user says no → assume privkey compromised, rotate creds, drain remaining
   balance to a fresh wallet immediately, update `nookplot_wallets.json`.

Cluster wallets W1–W12 store their addrs in `~/.hermes/nookplot_wallets.json`
under the `addr` field — easy to check whether a sink matches one of our own
wallets:

```python
sink_lower = sink_addr.lower()
ours = [k for k,w in wallets.items() if w['addr'].lower() == sink_lower]
if ours:
    print(f"sink is OUR wallet {ours[0]}")  # benign cluster sweep
else:
    print("sink is EXTERNAL — confirm with user")
```

## TL;DR template reply

When user says "reward gak masuk wallet X":

1. Hit Base RPC `eth_call balanceOf` for the wallet → fresh on-chain number.
2. Pull blockscout transfers → find the most recent `IN` from `0x3632428A`.
3. State the claim landed at `<timestamp>` with tx `<hash>` and current
   balance is `<n>` NOOK. `totalEarned` is lifetime, not current.
4. If gap exists, list the OUT destinations with classification.
5. Ask user to confirm any unclassified EOA sink; flag privkey-leak suspicion
   if denied.

Do NOT just say "refresh dashboard" without proving on-chain — user wants a
forensic answer, not a hand-wave.
