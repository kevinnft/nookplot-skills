# Multi-Wallet Pipeline State Recovery (post-compaction resume)

When the user asks the cluster to do something big — "selesaikan semua misi
guild deep dive", "audit semua wallet", "submit BCB ke semua wallet eligible" —
the work spans tens of REST calls and 30-90 min of composition. The
conversation context will compact at least once mid-pipeline. If pipeline state
lives only in the agent's tool-call history, the compaction summary will lose
the per-wallet allocation table, the IPFS CIDs you already uploaded, and the
trace markdown bytes — forcing you to redo the expensive parts.

## Rule: every multi-wallet pipeline checkpoints to /tmp BEFORE compaction risk

The expensive parts of any cluster pipeline are:
1. **Discovery + allocation** — which wallets are eligible, which guild, which
   tier, which slot is free, which challenges are open and not claim-locked.
2. **Trace composition** — 10-17K-char specialist markdowns grounded in the
   paper. ~3-8 min of generation per trace.
3. **IPFS upload result** — `trace_cid` + computed `trace_hash`. 2-5s each but
   irreplaceable; if you lose the CID you re-upload and produce a different
   one (paid call quota burn isn't the worry — it's the cognitive cost of
   re-doing the bookkeeping mapping wallet→trace_cid→submission_id).

Each of those goes to a named `/tmp/*.json` or `/tmp/*.md` file the moment it
is produced. NOT after the next step. NOT once the whole pipeline lands. Right
when the data exists in memory, write it to disk.

## Canonical /tmp layout for a multi-wallet pipeline

```
/tmp/<task>_plan.json        # allocation table: which wallet → which slot/role
/tmp/<task>_state.json       # tier/guild map, eligibility per wallet, claim locks
/tmp/<task>_papers.json      # full resource records (description, arxiv, github)
/tmp/<task>_<slot>.md        # per-slot composed trace markdown
/tmp/<task>_queue.json       # prepared_traces[]: cid, hash, target_wallet, trace_path
/tmp/<task>_results.json     # submitted: sid, status, http_code per slot
```

`<task>` is short and stable: `deepdive`, `bcb_batch`, `audit_15w`, etc.
`<slot>` ties to the allocation row: `A1_W6`, `A2_W11`, `B1_W7` — challenge
letter + slot ordinal + wallet id. Filename collisions across pipelines are
prevented by the prefix.

## First action of every resumed session: state-files audit

When a session opens with a context-compaction summary that mentions an
in-progress nookplot pipeline, the FIRST tool call is a state-files audit
before any new tool work:

```python
import os, json
expected = [
    "/tmp/deepdive_plan.json",
    "/tmp/papers.json",
    "/tmp/slot_state.json",
    "/tmp/guild_state.json",
]
for p in expected:
    print(f"{p}: {'OK' if os.path.exists(p) else 'MISSING'} "
          f"({os.path.getsize(p) if os.path.exists(p) else 0} bytes)")
```

Then dump the plan + papers so the agent can ground new compositions without
re-fetching:

```python
plan = json.load(open("/tmp/deepdive_plan.json"))
papers = json.load(open("/tmp/papers.json"))
print(json.dumps(plan, indent=2))
for k, p in papers.items():
    print(f"\n=== PAPER {k} ===")
    print(p["title"])
    print(p.get("description","")[:3000])
```

Verified May 22 2026: this 2-call audit on resume restored full pipeline
context (allocation table for 9 slots, full abstracts for 3 papers, eligibility
matrix for 15 wallets) without re-running 11+ discovery REST calls. The full
audit recipe was preserved across the compaction precisely because the plan
+ papers files survived on disk.

## What does NOT belong in /tmp

- Raw API keys / private keys. Use the existing `~/.hermes/nookplot_wallets.json`
  and reference wallets by id (W1..WN) inside `/tmp/*.json`.
- Bearer tokens captured at runtime. Re-derive from `nookplot_wallets.json`
  on resume.
- Big paginated discovery payloads. Summarize down to the eligibility-decision
  fields you actually need (`tier`, `boost`, `guild_domains`, `slots_used_24h`).
  The full payload bloats the plan file and obscures what's decision-relevant.

## Compaction-aware reporting

When the conversation compacts mid-pipeline, the next session opens with a
prose handoff. Bias that handoff toward facts the resume needs: file paths,
slot-allocation table, what is COMPLETE vs PENDING, what is BLOCKED. Avoid
restating reasoning chains — the disk state is the source of truth, the
handoff just points at it.

Pattern, embedded in the active task summary:
```
## Active State
- /tmp/<task>_plan.json — allocation, N slots
- /tmp/<task>_papers.json — full abstracts for N papers
- All eligibility probes complete; all M wallets FREE
- 0 traces written yet, 0 submitted

## Remaining Work
1. Compose N specialist traces
2. Upload to IPFS, compute hashes
3. Submit via REST, capture sids
```

The next session reads this, runs the state-files audit, confirms the disk
state matches the summary, and resumes at step 1 without re-doing discovery.

## Verified May 22 2026

Session opened mid guild-deep-dive pipeline (3 challenges × 3 wallets = 9 slots).
Compaction-recovery audit restored:
- 15-wallet eligibility matrix (W1..W15 tier/guild/boost)
- Allocation table A→[W6,W11,W2], B→[W7,W12,W10], C→[W8,W9,W14]
- Full abstracts for 3 papers (1.2K-1.8K chars each) — sufficient grounding to
  begin composition without re-fetching `/v1/resources/<rid>`
- 0 lost research; resume position confirmed at "compose 9 traces" step

State files used: `/tmp/deepdive_plan.json`, `/tmp/papers.json`,
`/tmp/slot_state.json`, `/tmp/guild_state.json`. Total disk footprint ~22KB
for what would otherwise be 11 redundant REST calls + duplicate token spend.
