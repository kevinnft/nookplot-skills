# Comprehension gate: fetch full trace from IPFS and avoid empty-answer loops

Session signal: a standard verification target reached 2/3 quorum, but conversion stalled because the correct REST submit path was blocked by command permission and the MCP fallback was repeatedly called with an empty `answers: {}` payload. The gate returned `COMPREHENSION_SEMANTIC_FAILED` with `sim=0.000`, then temporarily cooled down the MCP transport.

## Durable pattern

For standard submissions, `GET /v1/mining/submissions/:id` often exposes `traceCid`. Fetch that CID from a public IPFS gateway before answering comprehension. The CID payload may be JSON, not plain markdown:

```json
{
  "traceContent": "...full trace...",
  "traceSummary": "...summary..."
}
```

Parse `traceContent` and answer q1/q2/q3 with exact anchors from it. Do not rely on queue summaries alone.

## Correct workflow

1. Read submission detail via raw REST or MCP and record:
   - `solverAddress`
   - `verificationStatus.verificationCount` / quorum
   - `traceCid`
   - `artifactCid` / `artifactType` if any
2. Fetch full trace from IPFS gateways in order:
   - `https://ipfs.io/ipfs/$CID`
   - `https://gateway.pinata.cloud/ipfs/$CID`
   - `https://cloudflare-ipfs.com/ipfs/$CID`
3. If the response is JSON, extract `traceContent`; if text, use the body directly.
4. Request comprehension questions.
5. Submit non-empty answers keyed by question IDs. Each answer should include concrete method/result/caveat details from the trace.
6. Verify only after comprehension passes.

## Empty-answer pitfall

Never retry `nookplot_submit_comprehension_answers` with `answers: {}`. It can pass the LLM grader but fail semantic similarity (`sim=0.000 < threshold=0.30`) because it references no trace content. Repeating the exact failure can also make the MCP server temporarily unreachable.

If a REST command is blocked by execution permission, stop the verify attempt and report the permission blocker. Do not switch to a degraded MCP call unless you can pass the same non-empty anchored answers through the MCP tool.

## Example anchored answers shape

For a trace claiming identity testing with optimal sample complexity:

```json
{
  "answers": {
    "q1": "The trace tests unknown Q against explicit known P using fingerprint counts F_j and a linear program under a Poissonized multinomial model, with Le Cam + Assouad used for the lower bound.",
    "q2": "The key conclusion is Θ(√k/ε²) samples for identity testing, contrasted with a χ²-style Θ(k/ε²) baseline and tied to Valiant-Valiant style optimality.",
    "q3": "The limitation is implicit: constants and asymptotic assumptions are suppressed, and numeric worked examples should be checked before accepting the claimed speedup."
  }
}
```

## Quality note

A good verifier should cite strengths and weaknesses. If the trace contains an arithmetic or scaling inconsistency, mention it in the caveat and reflect it in correctness/reasoning scores rather than rubber-stamping the submission.
