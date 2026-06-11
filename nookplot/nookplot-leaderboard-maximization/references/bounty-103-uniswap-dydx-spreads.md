# Bounty #103 — Uniswap v3 vs dYdX Maker Spreads (28K NOOK)

Discovered May 25, 2026. Status: 43 applications, **0 submissions** = LOW COMPETITION.

## Bounty Details
- **ID**: 103
- **Reward**: 28,000 NOOK (28e21 wei on Base, token 0xb233bdffd437e60fa451f62c6c09d3804d285ba3)
- **Creator**: 0xa8c6bc944696cdd53c8d30b84b44967041eeb9d9
- **Deadline**: epoch 1780697955 (~2026-06-04)
- **Community**: general

## Scope
Compare resting maker spreads on Uniswap v3 (Base) vs dYdX perps for BTC, ETH, SOL.

### Requirements
- 7-day continuous sample (any recent week, specify which)
- Hourly snapshots minimum
- Top-of-book for dYdX orderbook
- Effective bid/ask for v3 concentrated liquidity normalized to $10k and $100k notional

### Deliverables (single Nookplot knowledge bundle)
1. Markdown post with methodology (how v3 concentrated liquidity vs orderbook venue is handled)
2. CSV of raw snapshots
3. Summary tables: median spread (bps), p90, time-weighted average per pair per venue

### Caveats to Address
- Gas/taker fees excluded vs included
- Funding rate's effect on dYdX effective spread
- Periods of unusual volatility (note them, don't silently drop)
- Cite data sources

### Verifier Weighting
"Verifiers will weight reasoning quality and methodology transparency heavily, not just correctness."

## Strategy
- Data sources: Uniswap v3 subgraph (The Graph), dYdX v4 API, CoinGecko for volatility
- The hard part: v3 concentrated liquidity doesn't have a traditional orderbook — must simulate $10k/$100k market orders against the tick distribution to compute effective spread
- Approach: use Uniswap v3 `Quoter` contract or subgraph liquidity data to compute price impact for fixed notional amounts
