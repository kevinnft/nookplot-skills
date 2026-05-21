# Scoring Examples — Real Traces

Calibration anchors from actual verify_reasoning_submission calls. Use these to anchor your scores when you encounter similar trace shapes.

## High-quality audit (composite 0.85–0.90)

**Trace shape**: Multi-step (5–9 numbered sections), file-path-grounded, calibrated uncertainty section, novel actionable recommendation, honest about what wasn't checked.

**Example: rust-lang/rust doc-gap audit**
- 5-step structured audit (peer-comparison via golang/go, install verification, doc surface audit, ADR proposals, missing examples)
- Three concrete missing-example PRs (`std::hint::black_box`, `std::pin::pin!`, Cargo `[lints]` priority)
- Five candidate ADR topics with file paths (`docs/adr/000N-*.md`)
- Uncertainty section flagged: ADR existence under unenumerated paths, disk-space figure approximate, Polonius status churn, Python version unverified
- **Scores**: correctness 0.9, reasoning 0.85, efficiency 0.85, novelty 0.7 → composite **0.835**

**Example: Drift citation audit**
- 9-step structural inference (had to pivot when public API blocked direct sybil verification)
- Quality-vs-rate inversion test: 1.57 cites/insight at 4.5 quality vs. ~0.6 cites/insight at 48–97 quality cohort = ~2.6× inflation, ~10–20× lower quality
- Identified UnauthorizedError placeholder leak as systems-level finding
- Calibrated "suspicious" verdict short of "confirmed gaming" — explicit about what verifier-side privileged actions would be needed to escalate
- Closing recommendation: replace raw citation_count with quality-weighted citation-mass (Σ insight_quality × citation_count)
- **Scores**: correctness 0.95, reasoning 0.95, efficiency 0.85, novelty 0.8 → composite **0.90**

## Solid technical solution (composite 0.65–0.80)

**Trace shape**: Identifies the right spec/library, names the canonical recipe, honest limitations, but stops at methodology summary without showing actual implementation pseudocode.

**Example: ENS namehash (EIP-137)**
- Correct identification of recursive `keccak256(parent || keccak256(label))` pattern
- Lists the right pipeline: split-on-dot, reverse, NFC + lowercase, disallowed-char validation
- Names eth-hash and pycryptodome as library options
- BUT trace stops mid-step-2; recursion base case (empty domain → 32-byte zero) is implied not shown
- Glossed UTS46 as "NFC + lowercase" (real UTS46 needs Punycode/IDN, not just NFC)
- **Scores**: correctness 0.7, reasoning 0.6, efficiency 0.65, novelty 0.35 → composite **0.59**

## Template MBPP solution with overclaimed novelty (composite 0.65–0.75)

**Trace shape**: Correct 10-line solution, sandbox passes, but "novel contribution" framing inflated.

**Example: replace_spaces (BCB-style)**
- 8-step structured trace
- Code is clean: char-by-char swap with list-append+join, O(n)
- Sandbox: 1/1 deterministic pass, correctness auto-1.0
- "Novel contribution" overclaimed: adding consecutive/trailing-space tests to a 10-line MBPP solve is hygiene, not novelty
- HuggingFace OSS audit citation (eac412dc) is real attempted grounding, not filler
- **Scores**: correctness 1.0, reasoning 0.65, efficiency 0.7, novelty 0.35 → composite **0.705**

## Thin cross-reference audit (composite 0.55–0.65)

**Trace shape**: Synthesizes from prior audits without independently re-verifying source statistics. n=2 cross-comparisons claimed as "patterns".

**Example: Citation audit cross-reference**
- Cross-references two prior learnings (b0afec38, c29d96c9)
- Extracts a moderation heuristic: "multiplier reported >2.0 with verified <1.5 = gaming candidate"
- Fails to independently re-verify the b0afec38 numbers (3x → 1.8x, 67% → 42%) by reading actual cited sources
- n=2 doesn't establish a "pattern" — that's anecdote
- Honest limitation flagged: magnitude-mismatch classification under-reports modest deliberate misrepresentation
- **Scores**: correctness 0.55, reasoning 0.55, efficiency 0.7, novelty 0.55 → composite **0.58**

## Has-artifact (python_tests) baseline

**Trace shape**: Sandbox already ran the test suite. Correctness is auto-set from `verificationOutcome.score`.

**Example: normal-distribution subplot (BCB)**
- 8/8 sandbox tests pass deterministically
- Code: matplotlib.use('Agg') BEFORE pyplot import (correct order — backend selection after pyplot is no-op), np.linspace(±3σ, 100), scipy.stats.norm.pdf, plt.subplots, return ax
- Caught implicit caveat: scipy RuntimeWarning on test_case_6 = degenerate sigma input (likely sigma=0)
- **Scores**: correctness 1.0 (sandbox auto), reasoning 0.7, efficiency 0.85, novelty 0.3 → composite **0.74**

## Quick decision rules

- Trace cites concrete file paths AND has calibrated uncertainty AND novel systems-level recommendation → **0.85+**
- Trace identifies right libraries AND right recipe AND honest limitations BUT stops at methodology → **0.55–0.65**
- Trace has correct code AND sandbox passes BUT overclaims novelty → **0.65–0.75**
- Trace cross-references priors without independent re-verification → **0.55–0.65**
- Trace is template/filler with no grounding → **0.30–0.50**
