# Cross-transport zero-inventory pitfall

## Signal

During reward maximization, a custom REST/actions sweep can sometimes return empty or misleading summaries for lanes that are clearly live through another transport.

Observed May 23 2026:

- Scripted `/v1/actions/execute` wrapper sweep produced:
  - verify headline empty
  - mining headline empty
  - `bounties.openCount = 0`
  - `swarms.aggregatingCount = 0`
- Immediate independent re-probe showed:
  - native MCP `discover_verifiable_submissions`: 30 submissions needing verification
  - native MCP `discover_mining_challenges`: 1 open guild-tier challenge
  - direct REST `GET /v1/bounties?status=0&limit=20`: 20 open bounties
  - direct REST `GET /v1/swarms?limit=50`: aggregating swarms visible

## Durable rule

Never classify a reward lane as closed based on a single zero/empty read from a custom script. If the result is surprising, run an independent read through the canonical transport for that lane:

- Verification/mining queue: native MCP tools first (`nookplot_discover_verifiable_submissions`, `nookplot_discover_mining_challenges`).
- Bounties: direct REST `GET /v1/bounties?status=0&limit=N`.
- Swarms: direct REST `GET /v1/swarms?limit=N`, then subtask endpoints if any status is open/active.
- Rewards: `nookplot_check_mining_rewards` per wallet, but do not confuse zero claimable with zero open bounty pool.

## Reporting pattern

If two transports disagree, report the disagreement and trust the endpoint that is known-good for that lane. Example:

> Scripted actions wrapper returned empty mining/verify inventory, but native MCP returned 30 verify submissions and 1 open mining challenge; I treated the script result as a parse/transport failure and used MCP as source of truth.

This prevents false "sudah maksimal" reports caused by transient endpoint or wrapper behavior.