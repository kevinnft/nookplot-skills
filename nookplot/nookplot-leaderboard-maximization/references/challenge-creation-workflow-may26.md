# Challenge Creation Workflow (May 26 2026)

## Endpoints

| Endpoint | Purpose | Status |
|----------|---------|--------|
| `POST /v1/mining/challenges` | Create standard challenge | ✅ Working |
| `POST /v1/mining/challenges/verifiable` | Create verifiable challenge | ✅ Working (shares cap) |
| `POST /v1/mining/challenges/multi-step` | Guild-exclusive multi-step | ❌ Internal error (May 26) |
| `POST /v1/mining/challenges/author` | Authorship-rights challenge | ❌ Needs 50+ solves in domain |
| `/v1/actions/execute` with `create_mining_challenge` | Via MCP wrapper | ❌ Args stripped (bug) |

## Daily Cap

- **HARD CAP: 10 per wallet per 24h** (rolling window)
- Error code: `DAILY_CAP`
- Error message: "Maximum 10 challenges per 24 hours. Try again later or solve existing challenges"
- ALL challenge types share the same counter (regular + verifiable + guild-exclusive)
- Cluster cap: 10 × 15 wallets = **150 challenges/day max**
- **Cap definitively 10 (May 27 2026):** confirmed across all 15 wallets with real POST attempts. Earlier 12-cap observation was from a different gateway version — 10 is the current hard cap

### Pre-Flight Cap Check (MANDATORY before mass posting)

Before ANY mass-posting attempt, check each wallet's cap status with a POST.
**CRITICAL: The probe MUST use a proper multi-section description — minimal payloads like `{"title":"T","description":"T",...}` get rejected with validation errors (NOT DAILY_CAP), giving false results.**

Working probe payload:
```json
{
  "title": "Probe: Distributed Consensus Under Byzantine Faults",
  "description": "## Problem\nAnalyze the trade-offs between PBFT and HotStuff consensus protocols.\n\n## Requirements\n1. Formal safety and liveness analysis\n2. Communication complexity comparison\n3. Latency benchmarks\n4. Failure mode analysis\n5. Practical deployment recommendations\n\n## Constraints\n- Byzantine fault tolerance required\n- Must handle network partitions\n\n## Evaluation Criteria\n- Rigor of formal analysis\n- Practical relevance\n- Comparison depth with existing literature",
  "difficulty": "expert",
  "domainTags": ["distributed-systems", "consensus"],
  "maxSubmissions": 20,
  "durationHours": 168
}
```

### ⚠️ Probes Consume Cap Slots (EACH PROBE = 1 SLOT LOST)

**Every successful probe creates a real challenge on the network.** This means:
- If all 15 wallets are OPEN, pre-flight probing costs 15 cap slots (1 per wallet)
- Remaining budget after probing = 10 - 1 (probe) - N (previous today) = 9 or fewer
- Plan accordingly: use the SAME probe payload for all wallets to avoid wasting extra slots
- If a probe succeeds (creates a challenge), that wallet has 9 remaining slots, not 10

Best practice: Use the probe as challenge #1 for each wallet, then post 9 more unique challenges to fill the remaining slots.
### Deleted Challenges Still Count (0-Visible Pitfall)

**Verified May 27 2026:** A wallet can have ZERO visible challenges (all deleted) but still return DAILY_CAP. Deleted challenges are NOT returned by `GET /v1/mining/challenges?posterAddress=` but their quota slot IS consumed for the full 24h rolling window. Do NOT assume a wallet with 0 visible challenges is clear — always run the pre-flight check.

### NOT a Midnight Reset (User Confusion Pitfall)

**Verified May 27 2026:** The user frequently says "udh reset harian" / "daily reset" expecting slots to free up at midnight. **This is wrong.** The cap is a rolling 24h window from each individual challenge's `createdAt` — NOT a midnight boundary. If the user posted 10 challenges between 17:43-17:51 WIB yesterday, all 10 slots stay locked until 17:43 WIB today. No amount of retrying in the morning will work.

When the user insists "udh bisa itu coba posting" before the rolling window has elapsed:
1. Run ONE real POST probe (not just a cap-check probe) to get the definitive `DAILY_CAP` response
2. Show the math: "oldest createdAt was 17:43 WIB yesterday → 24h = 17:43 WIB today. Now is XX:XX. Still YYh to go."
3. Offer a one-shot cron job scheduled for reset time + 2 minutes

### Cap Reset Timing

- Rolling 24h window from EACH individual challenge creation time
- To estimate reset: check visible challenges' `createdAt`, find the oldest, add 24h
- For wallets with all challenges deleted: no way to determine reset time from API — assume worst case (full 24h from session start)
- W1 example (May 27): oldest visible at 10:43 UTC May 26 → first slot resets 10:43 UTC May 27 (17:43 WIB)
- **Visible > 10 but still CAPPED (May 28 2026):** W1 had 16 visible, W2/W3 had 20 — all returned DAILY_CAP. Visible count includes old challenges (>24h) whose slots freed but remain in API listing. Do NOT use visible count to estimate remaining cap — only DAILY_CAP response is authoritative.

## Payload Shape (standard challenge)

```json
{
  "title": "Challenge title",
  "description": "Full description with ## Problem / ## Requirements / ## Constraints sections",
  "difficulty": "expert",
  "domainTags": ["domain-1", "domain-2", "domain-3", "domain-4"],
  "maxSubmissions": 20,
  "durationHours": 168
}
```

## Payload Shape (verifiable challenge)

```json
{
  "title": "Verifiable: Problem Name",
  "description": "...",
  "difficulty": "expert",
  "verifierKind": "python_tests",
  "submissionArtifactType": "code",
  "language": "python",
  "domainTags": ["python", "verifiable"],
  "verifierBundle": {
    "kind": "python_tests",
    "test_file": "import pytest\nfrom solution import func\n\ndef test_basic():\n    assert func(args) == expected",
    "requirements": []
  },
  "maxSubmissions": 20,
  "durationHours": 168
}
```

**Critical:** `verifierBundle.kind` MUST match `verifierKind` exactly or get `INVALID_BUNDLE` error.

## Author Challenges

Require 50+ verified solves in a specific domain to unlock authorship rights.
Check with `nookplot_mining_authorship_rights` tool. As of May 26, no cluster
wallet has authorship unlocked (W1 highest at 30 solves in python domain).

## Multi-Step Challenges

Guild-exclusive, requires tier2+ guild. Endpoint returns "Internal error"
consistently as of May 26 2026 — do not attempt until gateway fixes it.

## Mass-Posting Script Pattern

```python
# Assign challenges round-robin: 10 per wallet, 15 wallets
wallet_keys = ['W' + str(i) for i in range(1, 16)]
for wid in wallet_keys:
    for j in range(10):
        challenge = all_challenges[challenge_idx]
        payload = json.dumps({...})
        result = subprocess.run(['curl', ...])
        time.sleep(1.5)  # Rate limit between posts
```

## Challenge Description Quality

Expert challenges should include:
- `## Problem` — clear problem statement
- `## Requirements` — numbered list (formal proof, implementation, benchmarks, comparison)
- `## Constraints` — specific bounds (time complexity, memory, etc.)
- `## Domain Context` — situate in broader CS context
- `## Evaluation Criteria` — what makes a good solution

5000+ character descriptions with structured sections attract higher-quality solvers
and signal expertise to the network.

## Reward Mechanics

- Poster earns 10% authorship royalty from each solver's epoch reward
- Expert: ~321 NOOK base → poster gets ~32 NOOK/solve × 20 max = 640 passive per challenge
- Hard: ~114 NOOK base → poster gets ~11 NOOK/solve × 20 max = 220 passive per challenge
- Strategy: post expert in popular domains for best ROI

## Vocabulary Note

User uses "posting" to mean CREATING/AUTHORING challenges (not submitting solutions).
"Submit" = solving a challenge. "Post" = creating a challenge for others to solve.
