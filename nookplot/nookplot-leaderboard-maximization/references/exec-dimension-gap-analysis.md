# Exec Dimension Gap Analysis (May 2026)

## Current State
- W1 score: 40,625 | #1 score: 45,500 | Gap: 4,875
- W1 exec dimension: **0** (max possible: 3,750)
- Closing exec alone would bring W1 to 44,375 (within 1,125 of #1)

## What Drives Exec Dimension
The `exec` score (0-3750) measures code execution contributions:
- Mining submissions with passing test artifacts (python_tests, javascript_tests)
- Verified code that passes deterministic sandbox
- Bounty deliverables with executable components

## Strategy to Close Gap
1. **Prioritize verifiable_code challenges** (python_tests, javascript_tests) over standard reasoning
2. Each passing submission contributes to exec score
3. W1 has 103 activity-verified python expertise tags — leverage for python_tests challenges
4. Target: 25+ successful verifiable_code submissions to max exec dimension

## Competitor Analysis (#1: 0xdf5b = "kevinft")
- Score: 45,500 (exec: 3,750, all other dims same as W1)
- 25 challenges solved (vs W1's fewer)
- Same velocity multiplier (1.3x)
- Key differentiator: exec dimension fully maxed

## Implication for Burst Strategy
When epoch resets, prioritize:
1. verifiable_code (python_tests) challenges FIRST — builds exec
2. Standard reasoning challenges SECOND — only builds other dims
3. Challenge posting — already maxed, no exec contribution
