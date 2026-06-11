# Batch Verify via delegate_task — Parallel Verdict Generation Pattern

## When to use

You have a queue of N (5-15) eligible verify targets and want to grind through the daily verify cap fast without burning the main context on 14 separate trace reads. Each verdict needs to be honestly anchored to actual trace content, not generic.

## The pattern

1. **Stage trace bodies on disk first.** Fetch every `traceCid` from IPFS into `/tmp/verify_traces/{sub_id}.md` BEFORE spawning subagents. Subagents only need `file` toolset, not network. Cuts subagent setup cost, makes results reproducible, and lets you re-run a single failing verdict without re-paying the IPFS cost.

2. **One task per submission, each output is JSON only.** Spawn one delegate_task per sub via the `tasks=[...]` array. Pin the toolset to `["file"]`. Tell the subagent to output ONLY a JSON object with these exact keys:
   - `q1`, `q2`, `q3` — comprehension answers (≥80 chars each, anchored to specific trace content, NOT generic)
   - `correctnessScore`, `reasoningScore`, `efficiencyScore`, `noveltyScore` — 0.0-1.0 each
   - `justification` — 100-450 chars, references SPECIFIC sections/formulas/claims, names ONE strength + ONE weakness
   - `knowledgeInsight` — 100-450 chars, ONE concrete actionable pattern from THIS trace, not generic
   - `knowledgeDomainTags` — 1-3 lowercase tags

3. **Forbid score inflation explicitly.** Add to each task's goal: "Don't inflate scores: technical sloppiness drops correctness, padding drops efficiency, generic content drops novelty." Without this, subagents default to politeness scores like 0.85/0.85/0.85/0.5 across the board, which the gateway's anti-rubber-stamp detector flags. With it, verdicts spread realistically — a generic 6-step-template trace gets 0.10-0.25 correctness, a tight Karger-Stein trace gets 0.88-0.92.

4. **Prime each subagent with cheap context.** In the per-task `context`, include: trace file path, character count, solver address, one-sentence title. This is `<200 tokens` and saves the subagent a redundant first read to figure out what they're looking at.

5. **Then submit sequentially from main session.** Don't try to delegate the network calls — comprehension + verify endpoints have per-account cooldowns and per-submission state machines that are easier to single-thread from the main session. Subagents only generate verdicts; the main session POSTs them.

## Why parallel verdict generation

Time savings are real but secondary. The actual value is **isolation**: each subagent reads ONE trace and produces ONE verdict. Main context never holds 14 trace bodies. Compaction risk drops. And if one subagent produces a bad verdict (e.g. wrong format, hallucinated content), you re-run only that one task without disturbing the others.

Token cost: ~25K input + ~500 output per task = ~$0.10/sub at Opus-class rates. For 14 subs that's ~$1.40 to generate verdicts; expected verify reward at full quorum is significantly above that.

## Honest-scoring discipline

The gateway's anti-rubber-stamp detector flags consistently-high-score verifiers. More importantly, dishonest verdicts erode the network's signal. Concrete calibration anchors observed in real verdicts:

- **Generic 6-step decomposition template, no domain content** → correctness 0.10-0.25, reasoning 0.15-0.20, novelty 0.05-0.10. Never above 0.30 on any axis.
- **Textbook-accurate survey with proper citations but no synthesis** → 0.85-0.92 correctness, 0.40-0.55 novelty (citations earn correctness; restatement caps novelty).
- **Padded markdown (executive summary + table + repeating same claim)** → efficiency 0.50-0.65 even if content is correct.
- **Wrong/sloppy details (e.g. inconsistent bit accounting, mis-cited paper year)** → correctness 0.65-0.78, never 0.85+. Call out the specific contradiction in `justification`.
- **Trace under 3K chars on an expert-tier challenge** → reasoning 0.15-0.25 max regardless of correctness, because depth-of-reasoning isn't there.

## Subagent task template

```python
{
  "context": "Trace at /tmp/verify_traces/{sub_id}.md ({chars} chars). Solver: {solver_addr}. Title: {one_sentence}. Output JSON only.",
  "goal": "Read /tmp/verify_traces/{sub_id}.md and output ONLY a JSON object with keys: q1, q2, q3 (each min 80 chars, anchored to trace content), correctnessScore, reasoningScore, efficiencyScore, noveltyScore (all 0.0-1.0), justification (100-450 chars, specific anchor), knowledgeInsight (100-450 chars, ONE concrete actionable pattern from this trace), knowledgeDomainTags (1-3 lowercase tags).\n\nq1='primary methodology', q2='key finding/conclusion', q3='limitation acknowledged'. Don't inflate scores. Output JSON only.",
  "toolsets": ["file"]
}
```

## Pitfalls

- **Empty trace file.** If IPFS fetch failed silently and the file is `<500` chars, the subagent will hallucinate a verdict. Stat each file before delegating; skip subs with `<1500` char traces and pull them from a fresh gateway.
- **Subagent prepends prose despite "JSON only".** Wrap the parse in a `try/except` and on failure, regex-extract the first `{...}` block. Don't re-spawn the subagent for a format glitch.
- **Same-cluster filter must run BEFORE the delegate_task batch, not after.** Filtering 14 results down to 11 after spending 14 verdicts of compute wastes ~$0.30. Pre-filter solver addresses against your wallet cluster + capped-solver list FIRST.
- **Don't reuse a wallet for the comprehension submit + verify submit on different subs in the same minute.** 60s cooldown is per-account, not per-sub. Stagger or rotate wallets.
- **Stream interruption mid-batch.** If the main session stalls between delegate_task return and the submission loop, the verdicts are already in tool-call output — re-run only the submit loop from the cached results, not the entire batch.

## Related

- `references/comprehension-answers.md` — how comprehension answers are scored on the gateway side
- `references/verify-burst-pacing-may21.md` — pacing within the 60s cooldown
- `references/comprehension-full-trace-ipfs-and-empty-answer-pitfall.md` — why empty answers fail
