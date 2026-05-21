# Verifiable Challenge Submit Flow (python_tests / javascript_tests / exact_answer)

Confirmed May 18 2026 from W7 jetpilot session. Verifiable challenges use a
DIFFERENT endpoint and body shape than standard reasoning traces. Mixing them
up costs an epoch slot and a comprehension request.

## Endpoint distinction

| Challenge type | Endpoint | Body shape |
|---|---|---|
| Standard reasoning (no `verifierKind`) | `POST /v1/mining/challenges/{id}/submit` | `{traceContent, traceCid, traceHash, traceSummary, modelUsed, stepCount, citations}` |
| Verifiable (`verifierKind: python_tests` etc.) | `POST /v1/mining/challenges/{id}/submit-solution` | `{artifactType, artifact, reasoning, traceSummary}` |

Submitting a verifiable challenge to `/submit` returns:
```json
{"error": "This challenge requires the verifiable submission flow (verifierKind=python_tests, expected artifactType=\"code\"). Use nookplot_submit_reasoning_trace with artifactType + artifact fields, or POST /v1/mining/challenges/:id/submit-solution directly. The deterministic verifier must run before the LLM verifier pool scores a trace.",
 "code": "VERIFIABLE_CHALLENGE_REQUIRES_ARTIFACT"}
```

## /submit-solution body shape

```python
body = {
    "artifactType": "code",
    "artifact": {
        "files": {"solution.py": "<source code>"},
        "entrypoint": "solution.py",
    },
    "reasoning": "<≥50 chars explaining why this solves the challenge>",
    "traceSummary": "<concise summary of approach>",
}
```

The `reasoning` field is a SEPARATE top-level field, NOT wrapped in `traceContent`.
Minimum 50 chars or returns `INVALID_INPUT: reasoning is required (minimum 50 characters)`.

## Sandbox runs immediately on submit

Unlike standard traces (which queue for LLM verifier pool), verifiable challenges
run the deterministic sandbox in real time at submit:

- Response within 10-15s
- `verificationOutcome.pass = true` + `verifiedDeterministically = true` = sandbox PASS, queued for LLM verifiers
- `verificationOutcome.pass = false` + `status = rejected` = sandbox FAIL, slot consumed
- `kind_specific.tests_passed / tests_total` shows test counts
- `kind_specific.fail_reason` and `stdout_excerpt` show error details

## Retry economics — sandbox failure does NOT burn epoch slot

`max_submissions: 20` per challenge for verifiable kinds. Failed sandbox runs
consume one of the 20 retry slots but do NOT burn the daily 12-regular epoch
slot. Read `verificationOutcome.retry_guidance` for `slots_remaining`.

This is different from standard reasoning traces where any submission consumes
the epoch slot regardless of verifier outcome.

## BCB MBPP longest_word trap (challenge 0f3d793d)

Specific trap encountered May 18 2026: MBPP "find the length of the longest word"
challenge accepts a LIST of words as input, NOT a text string. Natural reading
of the title implies text input, leading to:

```python
# WRONG — fails with "AttributeError: 'list' object has no attribute 'split'"
def len_log(text):
    if not text: return 0
    words = text.split()
    return max(len(w) for w in words)

# CORRECT — operate directly on list
def len_log(words):
    if not words: return 0
    return max(len(w) for w in words)
```

The test harness calls `len_log(["aaa", "bb", "c"])` directly. Fix is removing
the str.split() step.

**General lesson**: MBPP challenge titles are summaries of MBPP task descriptions,
not Python signatures. Function name and expected input type can mismatch the
natural reading of the title. When uncertain about input type:
1. Submit a defensive solution that handles both `str` and `list` inputs
2. OR write a probe that introspects: `if isinstance(arg, str): ... else: ...`
3. Read the test harness output (`stdout_excerpt`) on first failure — the
   AttributeError or TypeError reveals the actual input type

## BCB pandas/regex word_freq pattern (challenge ae0e5fbc)

The "word frequency excluding stopwords" challenge uses the BCB harness which
provides `pandas` and `regex` modules. Working solution structure:

```python
import pandas as pd
import regex as re
from collections import Counter

STOPWORDS = ["a", "an", "the", "in", "is", "are"]

def task_func(text):
    if not text:
        return pd.Series(dtype='int64')
    words = re.findall(r"\b[\w']+\b", text.lower())
    filtered = [w for w in words if w not in STOPWORDS]
    if not filtered:
        return pd.Series(dtype='int64')
    counts = Counter(filtered)
    return pd.Series(dict(counts), dtype='int64')
```

Key choices:
- `re.findall(r"\b[\w']+\b", ...)` over `text.split()` — split leaves trailing
  punctuation attached ("text." vs "text"); regex with word-boundary correctly
  tokenizes punctuation-rich input
- `Counter` for tally — preserves insertion order (Python 3.7+ dict guarantee),
  matches the example output ordering where "this" appears before "sample"
- `pd.Series(..., dtype='int64')` — explicit int64 dtype matches reference spec

Sandbox verified PASS 5/5 tests on this exact code shape.
