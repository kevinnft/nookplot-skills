# RLM Challenge Format (verifiable_rlm)

**Status as of 2026-05-16:** Format unknown, needs reverse-engineering.

## Discovery

New challenge type `verifiable_rlm` appeared post-BCB era. Discovered via:

```
nookplot_discover_mining_challenges(verifierKind="rlm")
→ 49 challenges, all verifiable_rlm
```

## What we know

- `submissionArtifactType`: likely `"prediction_payload"` or similar (unconfirmed)
- `verifierKind`: `"rlm"` (not in the documented enum as of May 2026)
- Reward pool: 189,000 NOOK across 49 challenges (avg ~3,857 NOOK/challenge)
- Difficulty: mix of easy/medium/hard

## What we DON'T know

- Artifact schema — what fields does `artifact` object need?
- Submission flow — same as BCB (`submit-solution`) or different endpoint?
- Verification criteria — how are RLM submissions scored?

## Recommended research path

1. **Find existing submission** — search for agents who've solved RLM challenges:
   ```
   nookplot_discover(query="rlm", types="agent")
   nookplot_my_mining_submissions(address=<top-rlm-solver>)
   nookplot_get_reasoning_submission(submissionId=<rlm-submission-id>)
   ```

2. **Inspect artifact structure** — if submission detail includes artifact, reverse-engineer schema

3. **Test submit** — try submitting to an easy RLM challenge with best-guess format, read error message for hints

4. **Document format** — once confirmed, update this file + patch `nookplot-mine` skill (or create `nookplot-rlm-mining` if format is complex)

## Why not just try now?

User context: laptop sleeps often, limited resources, prefers evidence-based approach over trial-and-error. RLM research would take 1-2h with no guarantee of success. Better to wait for:
- Another agent to document the format
- Gateway docs to update with RLM schema
- User to explicitly prioritize RLM over other earning paths

## Related

- BCB format: `nookplot-bcb-mining` skill
- General mining: `nookplot-mine` plugin skill
- Verification: `nookplot-verification-mining` skill
