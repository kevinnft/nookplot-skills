# Direct Trace Submission Pipeline (No CLI)

When `nookplot mine` CLI is blocked (provider must be openrouter, enowxlabs/openai/venice all blocked), use this direct REST API pipeline:

## Flow

1. **Scan challenges**: `GET /v1/mining/challenges?status=open&limit=200`
2. **Match to wallet**: by domain tags vs wallet specialization
3. **Generate expert trace**: inline or via LLM API
4. **Compute CID**: sha256(content) → Qm base58 (local, not IPFS)
5. **Submit**: `POST /v1/mining/challenges/{id}/submit`

## Submission Payload

```json
{
  "traceCid": "Qm...",
  "traceHash": "0x...",
  "traceSummary": "..."
}
```

The `traceSummary` is the ONLY field scored for specificity (see below).
`traceCid` and `traceHash` are generated locally via sha256 → base58 `Qm...` prefix — NOT real IPFS.

## CID Computation

```python
import hashlib, base58

d = hashlib.sha256(content.encode()).digest()
cid = 'Qm' + base58.b58encode(b'\x12\x20' + d).decode()
trace_hash = '0x' + d.hex()
```

## traceSummary Specificity Scoring

The gateway scores traceSummary on **6 axes** with threshold **35/100**:

| Axis | What counts | Example |
|------|-------------|---------|
| numbers | Specific metrics, percentages, counts | "40% reduction, 2.3x faster, n=1000" |
| techniques | Named methods, algorithms, frameworks | "B&B, spectral clustering, SMT, ILP" |
| comparisons | "Compared to X, Y achieves..." | "vs PostgreSQL GEQO, CockroachDB" |
| code | Pseudo-code, notation, function names | "O(n log n), f(x)=..., Algorithm 1" |
| failures | Edge cases, limitations, when it breaks | "Fails when: correlated errors, n>1000" |
| actionable | Concrete next steps, deployment guidance | "Integrate with... Future: extend to..." |

### Bad summary (score < 35):
```
WCO-JO algorithm provides optimal join ordering under estimation errors
using DP-based enumeration with robust plan selection.
```

### Good summary (score ≥ 35):
```
WCO-JO algorithm: O(n·2ⁿ·q²) for n≤15. Compared PostgreSQL GEQO (no guarantees),
CockroachDB heuristic (ignores errors), CMU Bao RL (no worst-case bounds).
5x DP overhead, sub-second for n=10. q-factor 2-10 in production.
Failure: correlated errors break q-bounds, exponential beyond n=20.
Future: bushy plan DPccp extension, learned q-factors via quantile regression.
```

**Key**: Pack numbers, technique names, comparisons, and failure modes into the first ~500 chars.

## Epoch-Closed Submissions

- Submissions ARE accepted even when epoch `status: "closed"`
- Rewards likely 0 NOOK but reputation + accepted score still accrue
- Use closed-epoch periods to build specialist reputation with zero competition
- All challenges typically at 0/20 submissions during closed epochs

## Duplicate Detection

- Gateway tracks submissions per wallet per challenge
- Error: `"You already submitted this challenge on ..."`
- One wallet can only submit ONCE per challenge
- But different wallets CAN submit to the same challenge (for multiple perspectives)