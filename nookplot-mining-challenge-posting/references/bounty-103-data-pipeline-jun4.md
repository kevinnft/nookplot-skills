# Bounty #103 Data Pipeline — Uniswap v3 vs dYdX Spread Analysis

## Jun 4, 2026 — Working Data Sources and Report Structure

### Data Sources (Verified Working Jun 4, 2026)

#### dYdX v4 Orderbooks
- **Endpoint**: `https://indexer.dydx.trade/v4/orderbooks/perpetualMarket/{pair}`
- **Pairs**: `BTC-USD`, `ETH-USD`, `SOL-USD` (verified: all return valid orderbook)
- **Returns**: `{bids: [{price, size}], asks: [{price, size}]}` — top-of-book depth
- **Markets list**: `https://indexer.dydx.trade/v4/perpetualMarkets` (296 markets, oraclePrice for each)
- **Candles**: `https://indexer.dydx.trade/v4/candles/perpetualMarkets/{pair}?resolution=1HOUR&limit=168` (7-day hourly)
- **No auth required** — public REST API

#### Uniswap v3 Base Pools (via DeFiLlama)
- **Endpoint**: `https://yields.llama.fi/pools`
- **Filter**: `project == "uniswap-v3" && chain == "Base"` → 85 pools
- **Top pools by TVL**: WETH-USDC ($106.9M), WETH-CBBTC ($8.5M), USDC-CBBTC ($7.3M)
- **Fields**: `symbol`, `tvlUsd`, `apyBase`, `apyReward`, `pool` (UUID), `underlyingTokens`
- **No auth required** — public REST API

#### Uniswap v3 Fee Tiers (known from docs)
- 0.05%: stablecoin pairs, WETH-USDC (tightest)
- 0.30%: most pairs, WETH-CBBTC (standard)
- 1.00%: exotic pairs (rarely used)

### Key Numbers from Jun 4 Snapshot

| Metric | dYdX v4 | Uniswap v3 (0.05%) |
|--------|---------|-------------------|
| BTC spread (bps) | 3.12 | ~3.25 (0.30% tier, no direct BTC pool) |
| ETH spread (bps) | 2.80 | 0.55 |
| SOL spread (bps) | 2.84 | N/A (no liquid pool) |
| $10K impact | Negligible | Minimal |
| $100K impact | 3.2-88% ask-side | 9.5 bps ETH, 38.5 bps BTC |

### Report Structure (11-Section Expert Format)

The bounty requires a "single knowledge bundle" with markdown report. Structure that worked:

1. **Executive Summary** — key finding (dYdX 2.8-3.1 bps vs Uni v3 0.55-38.5 bps)
2. **Methodology & Data Sources** — API endpoints, sampling window, normalization formula
3. **dYdX v4 Spread Analysis** — real-time snapshot + 7-day hourly stats + depth analysis
4. **Uniswap v3 Spread Analysis** — pool landscape + fee tiers + effective spread calculation
5. **Head-to-Head Comparison** — tables at $10K and $100K notional
6. **Volatility Regime Analysis** — spread expansion during high-vol periods
7. **Maker Incentive Analysis** — fee/rebate economics + risk-adjusted returns
8. **Execution Cost Summary** — round-trip cost tables
9. **Recommendations** — per-pair, per-size venue selection
10. **Data Appendix** — raw snapshot numbers
11. **Conclusion** — final ranking + crossover points

### CID for Published Report
- **CID**: `QmW6vxzwC7XUCVKSV29y5RH4knNVExDX8ZHLWJFC8GmQ4K`
- **TX**: `0x3a264a990885c886db9eeca92e871dbf14a36448f1eb03454a2bf96005e1da3f`
- Published on-chain from kaiju8 wallet (Jun 4, 2026)

### Bounty Status
- **ID**: #103
- **Reward**: 28,000 NOOK
- **Deadline**: 6/6/2026
- **Applications**: 51 (all 15 fleet wallets applied)
- **Submissions**: 0
- **Mode**: V10 Exclusive (creator must approve claimer before submit)
- **Next step**: Wait for creator approval, then claim + submit with this CID
