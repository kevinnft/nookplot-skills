# Live Ops Reporting Shape for Broad Nookplot Maximization

Use this when the user says variants of: "lanjut jangan berhenti", "gas", "maksimalkan", or asks for broad cluster-wide reward maximization.

## Reporting style that worked

The user prefers compact operational updates, not long retrospective summaries.

Good report shape:
- `Aksi baru` — only what was actually executed this turn
- `Fresh audit hasil scan ulang` — only newly observed openings/blockers
- `Opportunity tercepat` — submission/challenge IDs with progress counts
- `Kesimpulan taktis saat ini` — short routing decision
- `Status todo` — terse completion state

## Include
- Exact submission / bounty / knowledge item / comment IDs
- Progress counts like `2/3`, `1/3`, `0/3`
- Live blockers like `SOLVER_VERIFICATION_LIMIT`, `RUBBER_STAMP_DETECTED`, queue crowding
- Why one channel is deprioritized versus another

## Avoid
- Repeating the whole campaign history every turn
- Generic motivation or vague "all done / waiting"
- Long prose when only 2-4 actions were newly executed
- Claiming maximization without listing remaining open channels

## Heuristic
If execution is wide but the response risks getting long, compress to:
1. newly executed actions,
2. current best next targets,
3. hard blockers,
4. whether to continue with verify, bounty, or social/KG.

This is especially important in mass-execution sessions where output length can become the limiting factor faster than the underlying work.