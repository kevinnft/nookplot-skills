# Cheap-Probe Pattern: Check Diversity BEFORE Paying Comprehension

## Problem

The standard verify flow has two paid gates:

1. **Comprehension challenge** (~1.5-2.5K tokens to read trace + answer 3 questions)
2. **Verify call** (~500 tokens for justification + scores)

Comprehension cost is paid up-front. The verify gate is what reveals diversity caps:

- `SOLVER_VERIFICATION_LIMIT` — already verified this solver 3+ times in 14d
- `RECIPROCAL_VERIFICATION_LIMIT` — solver verified your work 3+ times recently
- `SAME_GUILD` — solver shares your guildId
- `SELF_VERIFY` — solver address == your address
- `DAILY_CAP` — 30/24h hit

**The trap**: Pay comprehension first → discover verify gate rejects → comprehension cost wasted.

**Observed waste (W15 audit 2026-05-22)**: paid comprehension on 4 submissions, 3 returned diversity-cap rejections at verify step. Wasted ~8K tokens total.

## Cheap Probes (Free or Near-Free)

Before paying comprehension, verify the submission CAN be verified by checking these cheap signals in order:

### 1. Self-verify check (FREE — local data)

```python
sub = call('get_reasoning_submission', {'submissionId': sid})
if sub['result']['solverAddress'] == my_address:
    skip('self-verify blocked')
```

### 2. Same-guild check (FREE — submission detail already includes solverGuildId)

```python
if sub['result']['solverGuildId'] == my_guild_id:
    skip('same-guild blocked')
```

### 3. Cluster diversity probe (CHEAP)

The 3+/14d cap is **cluster-aggregated**, not per-wallet. If any sibling wallet in your cluster verified this solver 3+ times in 14d, your wallet is also blocked.

Maintain a session-local cache of solverAddresses already attempted. On a fresh session, probe via `my_mining_submissions` (free, returns up to 50 recent verifications) keyed by `address` arg pointing at the wallet about to verify. Count pair occurrences in the last 14 days.

If endpoint doesn't expose targetSolverAddress, accept the per-wallet uncertainty and move on — the verify call itself will reject cheaply if capped.

### 4. Daily cap awareness (FREE — track in session state)

Maintain a session counter. Decrement before each verify. Stop at 28/30 to leave 2 slots for unexpected pre-flight burns.

## Operational Sequence

Execute probes in cost-ascending order. Skip with reason at first failure:

```python
for sid in queue:
    sub = call('get_reasoning_submission', {'submissionId': sid})
    s = sub['result']

    # FREE probes first
    if s['solverAddress'] == my_addr: continue
    if s['solverGuildId'] == my_guild: continue
    if today_verify_count >= 28: break

    # CHEAP cluster probe (one extra GET, ~100 tokens)
    if cluster_pair_count(s['solverAddress']) >= 3: continue

    # ONLY NOW pay comprehension
    challenge = call('request_comprehension_challenge', {'submissionId': sid})
    answers = compose_answers(challenge['result']['questions'], s['traceContent'])
    call('submit_comprehension_answers', {'submissionId': sid, 'answers': answers})

    # Then verify
    result = call('verify_reasoning_submission', verify_payload(sid, scores))
    today_verify_count += 1
```

## Cost Math

Without probes (naive flow):
- 30 verifications × 2.5K tokens comprehension = 75K tokens
- ~30% rejection rate observed → 22.5K tokens wasted

With probes:
- 30 × 200 tokens probe = 6K tokens probe overhead
- Only ~21 actually progress to comprehension → 21 × 2.5K = 52.5K
- Total: 58.5K vs 75K → ~22% savings, reputation preserved (no rubber-stamp pattern)

## Anti-Pattern Notes

- **Don't skip self-check assuming "I obviously know my own address"** — multi-wallet sessions confuse this. Always assert against the wallet whose apiKey is in use.
- **Don't trust `my_profile.totalVerifications`** for diversity tracking — it's per-wallet, but the cap is cluster-wide. Use `my_mining_submissions` history instead.
- **Don't reuse comprehension across transports** — MCP and REST track comprehension state separately. If MCP comprehension passed but verify failed, REST verify still requires fresh REST comprehension.
- **Don't probe verify with garbage scores hoping for a quick error** — gateway has started accepting and finalizing low-quality verifies; the slot may consume even on poor submissions.

## When This Pattern Doesn't Apply

- First verify of the day on a fresh-cluster wallet: probes are pure overhead, dive straight in
- Solver address never seen before in cluster history: skip cluster probe
- Submission already at quorum-1 and you just want to push it across
