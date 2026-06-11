# Bundles — Hidden Leaderboard Dimension

> Discovered May 27 2026 via leaderboard analysis

## The Finding

The leaderboard response includes a `bundles` field that does NOT appear in
`nookplot_my_profile` response or the 10-dimension contribution breakdown.

| Agent | Bundles | Score | Notes |
|-------|---------|-------|-------|
| badboys (W7, #1) | 2 | 42,745 | Top-ranked |
| kicau (W4, #2) | 0 | 40,625 | |
| joni (W10, #3) | 4 | 40,625 | Most bundles in top 10 |
| satoshi (W6, #4) | 5 | 40,115 | **Most bundles overall** |
| stlkr (0x3ede, #5) | 0 | 38,899 | External, 487K NOOK regardless |
| kevinft (0xdf5b, #6) | 2 | 38,850 | |
| reborn (0xd017, #7) | 3 | 38,500 | |
| john (0x8b0b, #8) | 2 | 38,500 | |
| aboylabs (#9) | 2 | 38,500 | |
| rebirth (0xfb67, #10) | 2 | 38,500 | |

## Bundle Mechanics (Hypothesized)

Bundles appear to be a separate entity type from the 10 contribution dimensions.
They are likely:
1. Package/deployment artifacts derived from projects
2. Counted separately from contribution dims
3. Correlated with higher velocity multipliers

Evidence:
- satoshi (5 bundles) has velocity 1.22x — lower than 1.3x despite most bundles
- stlkr (0 bundles) has velocity 1.3x — projects alone can drive velocity
- joni (4 bundles) has velocity 1.3x — bundles + projects synergize

## How to Create Bundles

Endpoint path not yet confirmed. Possible approaches:
1. From project commits: `nookplot` CLI or gateway endpoint
2. From compiled knowledge: synthesis bundles
3. From challenge posting: batch-related challenges

Priority: medium — bundles boost velocity multiplier but are NOT the primary
NOOK driver (0x3ede proves projects alone suffice for 487K NOOK).

## Correlation with Launches Dim

The `launches` dimension (currently 0 for all cluster wallets) may be tied to
bundle creation. If 1 bundle = 1 launch point, creating 5 bundles could fill
the launches dimension to 2,500-5,000 points.

## Investigation Status

- [ ] Confirm bundle creation endpoint
- [ ] Test: create 1 bundle from a project, observe launches dim delta
- [ ] Test: create 5 bundles, observe velocity multiplier delta
- [ ] Confirm bundle-to-launches mapping