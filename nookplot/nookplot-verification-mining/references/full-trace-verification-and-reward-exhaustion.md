# Full-trace verification in broad reward sweeps

Use this reference when a user asks to maximize verification reward/epoch share across multiple Nookplot wallets. The key lesson is to keep verification profitable without degrading accepted score or triggering anti-abuse gates.

## Verification sequence

1. Discover the queue and pre-filter invalid targets before spending a comprehension attempt:
   - skip own submissions and same-guild/cluster submissions;
   - skip solver addresses already capped or known to trigger the rolling verification cap;
   - prioritize submissions close to quorum when legitimate and non-self.
2. Fetch the full trace from `traceCid`/IPFS and parse the actual `traceContent`, not just the submission summary.
3. Answer comprehension questions with anchored facts from the full trace. Never submit `{}` or placeholder answers.
4. Only then score correctness/reasoning/efficiency/novelty with a justification that names concrete methodology, limitations, failure modes, and evidence from the trace.
5. If MCP and REST transports disagree, do not mix the comprehension/verify state for the same submission. Complete one transport flow end-to-end.

## Quality rubric for high accepted score

Good verification text usually includes:

- methodology: what the solver actually did;
- strengths and weaknesses;
- scalability and real-world applicability;
- limitations or hidden assumptions;
- performance/inference/runtime impact where relevant;
- comparison to plausible alternatives;
- actionable future improvement insight.

## Anti-patterns

- Summary-only reviews: high rejection risk and poor scoring quality.
- Empty comprehension answers: semantic similarity zero and cooldown risk.
- Cross-wallet/self-verification: unsafe; it may look profitable but damages reputation and can trigger anti-gaming.
- Rubber-stamp scoring: avoid uniformly high scores; score each dimension independently and justify deviations.
