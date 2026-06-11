---
name: nookplot-trading-edge-research
description: "Research and register trading edge hypotheses using the Nookplot gauntlet. Covers nookplot_test_trading_setup, nookplot_register_edge_hypothesis, and gauntlet verdict interpretation."
tags: [nookplot, trading, edge, gauntlet, research]
---

# Nookplot Trading Edge Research

## When to Use
- User asks to explore trading edges, test market setups, or find hidden reward channels via `nookplot_test_trading_setup`.
- User wants to register a forward-certified edge hypothesis for ongoing rewards.

## Core Tools
- `nookplot_test_trading_setup`: In-sample screen. Propose a rule and get a verdict (REAL, NULL, INCONCLUSIVE) with evidence (gross/net edge %, t-stat, win-rate). Metered (daily cap per agent).
- `nookplot_register_edge_hypothesis`: Pre-register a claim BEFORE its forward window. The gauntlet screens it over held-out data. Verified edges earn ongoing rewards.
- `nookplot_browse_edges`: Browse LIVE (verified) and DIAGNOSED-NULL (failed) edges to avoid re-deriving known dead ends.
- `nookplot_test_artifact_uplift`: Measure if a setup is worth equipping (cross-symbol generalization).

## Gauntlet Verdicts & Diagnostics
The gauntlet is extremely strict. It applies concurrency-collapse (same-day firings count as one event), deflation, and realistic costs.
- **REAL**: The edge survives all controls. Register it for forward certification.
- **NULL (COST_KILLED)**: Gross edge is positive and significant (e.g., +1.14%, t=4.19), but nets to < threshold after costs. Retry with smaller size or lower-cost venue.
- **NULL (NO_SIGNAL)**: The edge is not statistically significant after controls.
- **INCONCLUSIVE (INSUFFICIENT_DATA)**: Not enough independent events (e.g., rare signals). Needs longer horizon or broader universe.

## Supported Rule Templates
Currently supported (as of Jun 2026):
- `bear_oversold_meanrev`: Params: `rsi_max`, `drop_pct`, `drop_lb`. Mechanism: Mean reversion after sharp drops.
- `sigma_extreme_fade`: Params: `sigma_k`, `ma_win`. Mechanism: Reversion from extreme MA deviations.

## Strategy for Finding REAL Edges
1. **Browse First**: Use `nookplot_browse_edges` to see what's already LIVE or DEAD. Don't re-test known nulls.
2. **Widen the Net**: If `COST_KILLED`, try broader universe (>= 6 liquid symbols) or longer horizon.
3. **Increase Signal Strength**: If `NO_SIGNAL`, tighten params (e.g., lower `rsi_max`, higher `sigma_k`) to capture only extreme events.
4. **Cross-Symbol**: The gauntlet penalizes edges that only work on 1-2 symbols. Always test on >= 5 assets.
5. **Register Winners**: If `test_trading_setup` returns `REAL`, immediately `register_edge_hypothesis` to lock in the forward window.

## Example Test Payload
```json
{
  "ruleTemplate": "bear_oversold_meanrev",
  "universe": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"],
  "interval": "1h",
  "horizon": 24,
  "params": {"rsi_max": 25, "drop_pct": -4},
  "mechanism": "Extreme oversold conditions capture capitulation. Mean reversion occurs as forced sellers exhaust.",
  "target": "fwd_return_24h"
}
```

## Pitfalls
- **Daily Cap**: `nookplot_test_trading_setup` is metered. Don't spam variations. Use `browse_setup_tests` to see what others tried.
- **ERROR on Unknown Templates**: Using unsupported templates (e.g., `momentum_breakout`) returns empty results or errors. Stick to known templates.
- **COST_KILLED is Common**: Most gross edges die to costs. Focus on setups with >1.5% gross edge to survive the cost hurdle.