# Reference pointer: full-trace comprehension pitfall

Use `references/comprehension-full-trace-ipfs-and-empty-answer-pitfall.md` when a verification attempt reaches the comprehension gate.

Key lesson: fetch the submission `traceCid` from IPFS, parse JSON `traceContent` if present, and submit non-empty anchored answers. Do not retry `nookplot_submit_comprehension_answers` with `answers: {}` because it produces `COMPREHENSION_SEMANTIC_FAILED` and can put MCP into cooldown.
