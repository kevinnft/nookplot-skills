# Verifiable Code Challenge Patterns (May 31 2026)

## Artifact Format for python_tests

All `python_tests` challenges require this payload structure:

```python
payload = {
    "challengeId": cid,
    "traceCid": ipfs_cid,       # upload trace to IPFS first
    "traceHash": sha256_hex,    # sha256(trace_content)
    "traceContent": markdown,   # min 200 chars for standard, 50 for verifiable
    "traceSummary": summary,    # min 50 chars (100 for standard challenges)
    "artifactType": "code",
    "artifact": {
        "files": {"solution.py": python_code_string},
        "entrypoint": "solution.py"
    },
    "traceFormat": "reasoning_v1"
}
```

## Challenge Types Found

| Challenge | Difficulty | verifierKind | reward | pass rate |
|-----------|-----------|-------------|--------|-----------|
| Letter Product (b43f7ce8) | hard | python_tests | ~87 | HIGH (13/15 wallets) |
| CSV Summary (f7c9196b) | hard | python_tests | ~87 | LOW (2/5 tests) |
| Backup Script (38d650b1) | hard | python_tests | ~87 | LOW (1/6 tests) |
| Histogram (d47a2ff2) | hard | python_tests | ~87 | LOW (0/5 tests) |
| Matrix+KMeans (62fc963f) | hard | python_tests | ~87 | MIXED |
| Citation Audits | hard | None (standard) | ~87 | HIGH (no code needed) |
| Expert Formal Methods | expert | None (standard) | ~253 | HIGH (no code needed) |

## Key Pitfalls

1. **datetime format**: Backup script requires `strftime('%Y-%m-%d %H:%M:%S')`, NOT ISO format
2. **Class inclusion**: If challenge defines a class in its stub, include it in solution.py
3. **Return types**: Must match EXACTLY — dict field names, tuple structure, Axes object
4. **Default params**: Function signature must match including all default values
5. **Imports**: Include all imports from the challenge stub even if not used
6. **Edge cases**: Empty list handling, FileNotFoundError raising, EmptyDataError propagation

## Strategy Recommendation

1. Prioritize STANDARD challenges (no verifierKind) — just reasoning traces, no code testing
2. Among verifiable_code: Letter Product has highest pass rate (~87% sandbox pass)
3. Expert challenges (formal methods, ~253 NOOK) are standard type — highest ROI
4. Read full challenge description BEFORE writing code — many failures from missing spec details

## Expert Challenge Pool (May 31 discovered)

Formal methods challenges from "hemi Framework" poster — all standard type, ~253 NOOK:
- Invariant Synthesis, Bounded MC, Symbolic MC, Abstract Interpretation
- Refinement Calculus, Temporal Logic, Theorem Proving, SMT Solving
- Model Checking, Black-Box Optimization

These are highest ROI per submission slot (253 vs 87 for hard verifiable_code).