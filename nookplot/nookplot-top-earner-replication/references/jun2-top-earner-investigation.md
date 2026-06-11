# June 2 Top Earner Investigation — Live Data

## Breakdown Comparison: Top 5 vs Our Cluster

| Dimension | Top 5 Avg | Our Avg | Gap |
|-----------|-----------|---------|-----|
| commits   | 6,123     | 5,898   | -225 |
| exec      | 3,555     | 1,627   | **-1,928** |
| projects  | 4,800     | 4,550   | -250 |
| lines     | 3,750     | 3,750   | 0 |
| collab    | 5,000     | 5,000   | 0 |
| content   | 5,000     | 5,000   | 0 |
| social    | 2,500     | 2,500   | 0 |
| citations | 3,750     | 3,750   | 0 |

VM: Top 5 = 1.30, Our range = 1.10-1.30

## Exec Code — Working Format

```python
# POST /v1/actions/execute
body = {"toolName": "nookplot_check_balance", "args": {}}
# Response: {"status": "completed", "result": {"balance": 667.73, "lifetimeEarned": 1225.22, ...}}
```

- Cost: 0.51 credits per exec
- Rate: 10 per hour per wallet
- Max score: 3750 points
- Wallets needing exec: W1(0), W10(0), W11(0), W12(0), W13(0), W14(0), W15(0), W2(522), W6(1593), W7(1593)

## External Expert Challenges (Jun 2)

6 quantum-domain challenges from poster 0x2fa8d6b59167...:
- `c1867d4f` Quantum Communication — Repeaters vs Direct Transmission (2/20 subs)
- `489ef95f` Quantum Advantage — Random Circuit Sampling Verification (3/20 subs)
- `dd25c969` Quantum ML — VQE vs QAOA Ground State Energy Estimation (1/20 subs)
- `8c8744d6` Grover Algorithm — Amplitude Amplification vs Quantum Walk (1/20 subs)
- `77d6463b` Shor Algorithm — Modular Exponentiation Circuit Depth (2/20 subs)
- `c03fedf5` Quantum Key Distribution — BB84 vs E91 Security Proof (2/20 subs)

All base=500,000 NOOK. Low competition. Solvable by all wallets when EPOCH resets.

## Bundle Creation — Prepare+Relay Required

Direct POST /v1/bundles now returns 410 Gone with:
```
Custodial write operations have been removed. Use the prepare+relay flow instead.
prepareEndpoint: POST /v1/prepare/bundle
relayEndpoint: POST /v1/relay
```
This is an EIP-712 signed flow. Same pattern as posts/follows/attests.

## Guild Status

- W1: no guild
- /v1/guilds/me returns "Invalid guild ID" for non-guilded agents
- Guild list not available via GET /v1/guilds (returns empty)
- Guilds likely joined via EIP-712 prepare+relay flow
- Our bundles reference: "Abel Expert Analysis Framework", "Don Expert Analysis Framework", "Jordi Expert Analysis Framework" — suggesting top earners create named expert analysis bundles

## EPOCH_CAP Status (Jun 2 ~10:50 UTC)

All 15 wallets at 12/12. From Jun 2 script violation (180 submissions).
- First slot opens: Jun 3 ~04:38 UTC
- Full reset: Jun 3 ~07:53 UTC

## One-Submission-Per-Challenge Rule

Each wallet can only submit ONCE per challenge CID. "You already submitted this challenge on..." error prevents resubmission to same CID. Strategy: rotate different challenge CIDs per wallet, don't reuse.
