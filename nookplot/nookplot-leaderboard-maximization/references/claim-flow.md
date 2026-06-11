# Nookplot Claim Flow Reference

## Tool Names (exact, as of May 2026)

| Tool Name | Purpose | Notes |
|---|---|---|
| `nookplot_claim_mining_reward` | Claim ALL mining rewards (epoch_solving + epoch_verification + guild_inference_claim) to wallet on-chain | No params needed; optional `sourceType` to claim specific pool. THIS is the main claim tool. |
| `nookplot_claim_reward` | Claim Merkle pool rewards (separate system) | Param: `pool: "nook"` or `"weth"`. Different from mining rewards. |
| `nookplot_claim_mining_pool_reward` | Claim from MiningRewardPool contract via Merkle proof | Needs `cumulativeAmount` + `proof[]` from `nookplot_get_mining_proof`. |
| `nookplot_claim_and_stake_mining_pool_reward` | Claim + auto-stake in one tx (compound) | No params — gateway auto-fetches Merkle proof. Fails if pending unstake exists. |
| `nookplot_claim_guild_mining_treasury` | Claim guild treasury share | Param: `guildId`. Must be member 24h+. |
| `nookplot_claim_pending_guild_mining_treasury` | Claim after being removed from guild | No guild membership needed. |
| `nookplot_claim_inference` | Claim guild inference fund NOOK | For covering reasoning costs. |
| `nookplot_ecosystem_claim_rewards` | Claim partner-protocol rewards (e.g. BOTCOIN) | Auto-detects finalized epochs if `epochIds` omitted. |

## Check vs Claim (Stale Data Caveat)

`nookplot_check_mining_rewards` can return stale/cached claimableBalance values. The actual `nookplot_claim_mining_reward` call is the source of truth — if it returns `NO_BALANCE`, the balance is truly 0 even if check showed non-zero amounts. This happens because:
- Epoch settlement may have already cleared the balance
- Cached data from a previous epoch

**Always verify with the actual claim tool, not just the check tool.**

## Dashboard Manual Claim

For manual claim via web UI:
1. Go to https://nookplot.com/join
2. Click "Sign in with API Key"
3. Paste the wallet's API key (from `nookplot_get_credentials`)
4. Navigate to Mining/Rewards section
5. Click claim buttons for available rewards

## Revenue Claim (Deprecated)

`POST /v1/revenue/claim` returns **410 Gone** — custodial writes removed. Must use prepare+relay flow instead. The prepare endpoint `/v1/prepare/revenue/claim` also returns 404 as of May 2026. Revenue claims may only work via dashboard.

## Merkle Mining Claim (prepare/mining/claim)

For accumulated mining rewards (dashboard "ON-CHAIN CLAIMABLE"):

1. Get proof: `POST /v1/actions/execute` `{"toolName":"get_mining_proof"}`
2. Prepare: `POST /v1/prepare/mining/claim` `{"cumulativeAmountRaw":"<raw>","proof":["0x...",...]}`
3. Sign + Relay: standard EIP-712 flow

**Pitfall (May 2026)**: `prepare/mining/claim` consistently fails with `"Failed to prepare mining reward claim"` (500) even with valid proof data (cumulativeAmountRaw + 10-element proof array + epochNumber + merkleRoot all tried). ALL payload variations rejected. Web dashboard claim button ALSO returns 500 with same error.

**Root cause identified May 31 2026**: The MiningRewardPool contract at `0x3632428A7adA9AB6fBD0C61d7eB119108Ba2C348` does NOT exist on Base mainnet (`eth_getCode` returns `0x`, length 2). The gateway's prepare step calls this contract to build the ForwardRequest, which fails because there's no contract to call. This is a platform-side issue — the contract may have been redeployed at a different address or removed entirely.

**All attempted variations that failed:**
- With/without epochNumber
- With/without merkleRoot
- cumulativeAmount (string) vs cumulativeAmountRaw (wei string)
- Via REST prepare + via actions/execute with nookplot_claim_mining_pool_reward
- Via claimAndStake endpoint (404)
- Web dashboard claim button (500)

**Status**: BLOCKED — requires Nookplot to fix/deploy contract or update gateway. No workaround available as of May 31 2026.

See `references/merkle-claim-prepare-failure-may31.md` for full failure analysis.

## Dashboard vs API Discrepancy (May 31 2026 Discovery)

**Symptom**: User sees "10.2k ON-CHAIN CLAIMABLE" on nookplot.com dashboard (`CLAIM - ON-CHAIN` section) but API `check_mining_rewards` returns all zeros (epoch_solving=0, epoch_verification=0, guild_inference_claim=0). Error 500 "Failed to prepare mining reward claim" when user tries to claim.

**Root cause**: Dashboard shows **Merkle pool rewards** (historical mining solves, already settled). The `claimableBalance` fields in API track **current epoch rewards** (not yet settled). These are different reward pools.

**Resolution paths:**
1. **Dashboard manual claim** (fastest) — user logs into nookplot.com → "Sign in with API Key" → paste wallet's API key → click Claim under CLAIM - ON-CHAIN section
2. **Add wallet PK** to `~/.hermes/nookplot_wallets.json` → enables EIP-712 signing for prepare+relay flow via `POST /v1/prepare/mining/claim` + relay
3. **Enable MCP Nookplot** → use MCP tools (`nookplot_claim_reward`, `nookplot_get_mining_proof`) which handle signing server-side

**W1 PK blocker**: W1 is MCP-bound with no private key in wallets.json (`pk` field absent). On-chain claims via prepare+relay require PK for EIP-712 signing. W1 can only claim via dashboard or MCP tools.

**Debug checklist when user says "di web ada X":**
1. `GET /v1/revenue/balance` — check claimable NOOK + ETH
2. `POST /v1/actions/execute {toolName:"check_mining_rewards"}` — check epoch balances
3. Identify which reward TYPE matches the web number (merkle pool vs epoch vs revenue)
4. If Merkle pool: user needs dashboard claim, PK setup, or MCP activation
5. If epoch: try prepare+relay; if NO_BALANCE, rewards already settled to merkle pool

## Batch Check Rate Limiting

When checking rewards across all 15 wallets:
- Sleep **3-4 seconds** between requests minimum
- Retry up to **5 times** on 502 gateway errors (exponential backoff: 5s + attempt*3s)
- Rate limit returns `"Too many requests"` — wait 5-10s and retry
- Gateway 502s are transient; all wallets eventually respond with patience
