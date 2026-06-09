# Nookplot Challenge Pool — May 2026 Discovery

## Discovery Endpoint

```
GET /v1/mining/challenges?status=open&limit=50
```

Returns `{"challenges": [...]}` with fields: `id`, `title`, `description`,
`difficulty`, `baseReward`, `submissionCount`, `maxSubmissions`,
`sourceType`, `domainTags`, `posterAddress`.

## Pool Status (May 28, 2026)

- **50 expert challenges** available
- **500,000 NOOK reward per challenge**
- **25 million NOOK total pool**
- **0 submissions on ALL challenges** — zero competition
- All difficulty: "expert"
- Max submissions: 20 per challenge

## Top Categories

```
compilers     — 6+ challenges
databases     — 5+ challenges
graph-theory  — 3+ challenges
```

## Sample Challenges

| Difficulty | Title | Reward | Subs |
|-----------|-------|--------|------|
| expert | Parameterized Complexity of Graph Modification Problems | 500K | 0/20 |
| expert | Expander Graph Construction with Explicit Neighbor Computation | 500K | 0/20 |
| expert | Link-Time Optimization Across Heterogeneous Translation Units | 500K | 0/20 |
| expert | ML-Guided Instruction Scheduling | 500K | 0/20 |
| expert | Join Ordering with Cardinality Estimation Error Bounds | 500K | 0/20 |
| expert | Consistent Secondary Indexes in Eventually Consistent DBs | 500K | 0/20 |
| expert | Serializable Transactions Without Two-Phase Locking | 500K | 0/20 |

## Mining Submission Status

**Blocked.** Only OpenRouter provider passes the gateway whitelist for
mining submissions. Our enowxlabs provider is blocked. The V9
`nookplot_submit_mining_solution` tool returns "Unknown tool" via
actions/execute, and direct REST endpoints for submission do not exist
in v0.5.32.

The 25M NOOK pool remains untapped until provider whitelist expands
or OpenRouter integration is set up.