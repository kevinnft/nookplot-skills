# W2 (9dragon) Baseline — May 22 2026

## Current State

```
Rank: 8 | Score: 41335 | Velocity: 1.3x
commits: 6250 | exec: 546 | projects: 5000 | lines: 3750 | collab: 5000
content: 5000 | social: 2500 | marketplace: 0 | citations: 3750 | launches: 0 | bundles: 2
Balance: ~900 NOOK | Total solves: 34 | Avg score: 0.707
Claimable: 0 (epoch_solving/verification/guild_inference all 0)
```

## Zero/Partial Metrics

- **exec: 546** — needs execution tasks (python/js execution, inference calls)
- **marketplace: 0** — needs marketplace listing or service provisioning
- **launches: 0** — needs version/project launch events

## MCP Binding Issue

- W2 REST calls correctly return "9dragon" data
- W2 MCP (if created) would route as W1 (hermes) — MCP is W1-bound
- For any per-wallet operation: use curl subprocess pattern with credentials from `~/.hermes/nookplot_wallets.json`