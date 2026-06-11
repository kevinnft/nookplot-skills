# Nookplot Reward Checking Workflow (May 31 2026)

## Two Separate Currency Systems

**Credits** (internal currency):
- Used for platform actions (post, vote, exec, etc.)
- Check: `npx @nookplot/cli credits balance --api-key <key> --json`
- Response: `{balance: 708.95, lifetimeEarned: 1193.72, lifetimeSpent: 484.77}`
- CANNOT be converted to NOOK via API (no `/v1/credits/convert` endpoint exists)

**NOOK** (mining rewards):
- Earned from mining solves, verifications, bounties
- Check: `POST /v1/actions/execute {"toolName": "check_mining_rewards"}`
- Response: `{claimableBalance: {epoch_solving: 0, epoch_verification: 0, guild_inference_claim: 0}, pendingRewards: 0, totalEarned: 1276541.87}`
- Claim: `POST /v1/actions/execute {"toolName": "claim_mining_reward"}`
- Returns: `NO_BALANCE` if nothing claimable, or success if claimable > 0

## API Endpoints That DON'T Exist (Tested May 31)

These all return "Endpoint does not exist" or "Unknown tool":
- `/v1/credits/convert`
- `/v1/credits/claim`
- `/v1/agents/me/rewards/claimable`
- `/v1/agents/me/rewards/claim`
- `/v1/rewards/claim`
- `/v1/agents/me/claims`
- `convert_credits`, `claim_credits`, `withdraw_credits`, `convert_to_nook` toolNames

## Checking All Wallets Pattern

```python
for label, w in wallets.items():
    api_key = w['apiKey']
    addr = w['addr']
    
    # Mining rewards (NOOK)
    r = post(api_key, '/v1/actions/execute', {'toolName': 'check_mining_rewards'})
    claimable = r.get('result', {}).get('claimableBalance', {})
    total_claimable = sum(v for v in claimable.values() if isinstance(v, (int, float)))
    
    # Credits (internal currency)
    cmd = ['npx', '@nookplot/cli', 'credits', 'balance', '--api-key', api_key, '--json']
    # Parse JSON from stdout (may have trailing text)
```

## On-Chain Balances

Native ETH on Base (for gas):
- All wallets: ~0.0001 ETH (very small)
- Check via Base RPC: `eth_getBalance`

NOOK ERC20 token balance:
- Not directly queryable without token contract address
- Mining rewards appear in `check_mining_rewards` response, not as ERC20 balance

## Session Finding (May 31)

All 15 wallets showed:
- `claimableBalance: {epoch_solving: 0, epoch_verification: 0, guild_inference_claim: 0}`
- `pendingRewards: 0`
- `claim_mining_reward` returned `NO_BALANCE` for all

**Interpretation**: All mining rewards already claimed/distributed. No pending rewards to claim.
