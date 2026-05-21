# Per-Wallet Autonomous Farming Loop

Pattern verified May 2026: cloning `np_w2_loop.py` template into a per-wallet `np_wN_loop.py` produces a stable nonstop farming loop for any wallet in the cluster. One Python process per wallet, one log + state file per wallet, no cron.

## When to use

User says any variant of:
- "wallet 6 nonstop", "kerjakan wallet X full auto"
- "FULL AUTO / MAXIMIZE REWARD" prompt
- A new wallet just got registered and needs to start earning while you do other things

When the user wants ONE wallet active continuously, this is the right shape. Each wallet gets its own loop process; they run in parallel without coordination because every action is rate-limited per wallet at the gateway.

## Template location

- Source template: `/home/asus/.hermes/scripts/np_w2_loop.py` (W2/9dragon, the original)
- Per-wallet copies: `/home/asus/.hermes/scripts/np_w<N>_loop.py`

## Clone procedure (verified working for W6 May 18 2026)

1. **Copy template via terminal `cp`** — do NOT `read_file` then `write_file` from the original. read_file redacts `Bearer ***` in curl headers and you'll write a broken script back.
   ```
   cp /home/asus/.hermes/scripts/np_w2_loop.py /home/asus/.hermes/scripts/np_w6_loop.py
   ```

2. **Patch credentials block** — replace the `~/.env` reader with embedded creds for the target wallet (only W2 lives in `~/.env` as `NOOKPLOT_AGENT_PRIVATE_KEY` etc; W3-W9 do not, per user preference May 2026: no new PKs persisted to ~/.env).
   ```python
   # ---------- credentials W6 satoshi ----------
   API_KEY = "nk_..."  # from ~/.hermes/nookplot_wallets.json
   PRIV    = "0x..."
   ADDR    = "0x...".lower()
   GATEWAY = "https://gateway.nookplot.com"
   ```

3. **Rename state + log paths** — every wallet must have isolated state. Concurrent loops sharing `/tmp/np_w2_state.json` will trample each other's `done_verifies` / `last_verify_ts` and trigger rate-limit avalanches.
   ```
   LOG = "/tmp/np_w<N>_loop.log"
   STATE_FILE = "/tmp/np_w<N>_state.json"
   ```

4. **Update banner** — `log(f"=== W<N> farming loop START — addr={ADDR} ===")` so log triage is unambiguous.

5. **Smoke-test before launch**:
   ```
   /home/asus/.hermes/hermes-agent/venv/bin/python -c "
   import importlib.util
   spec = importlib.util.spec_from_file_location('m','/home/asus/.hermes/scripts/np_w<N>_loop.py')
   m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
   print('ADDR:', m.ADDR)
   r = m.call('/v1/actions/execute', 'POST', {'toolName':'nookplot_my_profile','args':{}})
   print('auth ok' if r.get('result') else 'FAIL', str(r)[:200])
   "
   ```
   `auth ok` confirms credentials were copied correctly.

6. **Launch background** with `notify_on_complete=true` so a fatal crash alerts the user (loop should never naturally exit):
   ```
   terminal(background=true, notify_on_complete=true,
            command="/home/asus/.hermes/hermes-agent/venv/bin/python "
                    "/home/asus/.hermes/scripts/np_w<N>_loop.py >> /tmp/np_w<N>_loop.log 2>&1")
   ```

## Default action mix (verified produces NOOK)

```python
actions = ["verify", "verify", "verify", "store_kg", "comment", "verify", "claim"]
random.shuffle(actions)
```

Rationale:
- 4× verify per cycle — cap is 30/day with 60s cooldown; verify is the highest NOOK/cycle action when not gated. Cycle is roughly 5-15 min so this keeps verify-attempt rate well under the cap.
- 1× store_kg — citation rewards are unlimited; topics rotated from the template's hard-coded list keep the KG growing without spam patterns.
- 1× comment — engagement signal, capped at 80/day in the loop (network limit is 100/day).
- 1× claim — lightweight check; claims auto-fire when `claimableBalance` has any non-zero entry.

## Gate-handling outcomes

The loop's `attempt_verify()` returns these strings — keep them in sync if you fork:

- `verified` — success, append to `done_verifies`
- `skip_artifact` — submission has artifact (python_tests/exact_answer/etc.); skip until you wire artifact-aware scoring
- `skip_short` — trace too short to verify in good faith (< 500 chars)
- `skip_reciprocal` — `RECIPROCAL_VERIFICATION_LIMIT` (3 verifies per solver per 14d, bidirectional)
- `skip_diversity` — `SOLVER_VERIFICATION_LIMIT` / `DIVERSITY` (same gate from the other side)
- `rate_limit` — sleep 5min, then continue
- `rubber_cooldown` — `RUBBER_STAMP_COOLDOWN` 24h; pivot to non-verify actions

Any `skip_*` outcome appends to `skipped_subs` so the loop never retries the same gate-blocked submission.

## Pitfalls (verified May 2026)

- **DO NOT use raw `urllib` from `execute_code`** — gateway returns 403 without User-Agent. The loop uses `subprocess + curl` which works. If you need REST from `execute_code` for diagnostics, use `subprocess.run(['curl', ...])`, not `urllib.request`.
- **DO NOT use `curl --max-time 30` for `/v1/mining/challenges?limit=100`** — large JSON gets truncated to 500 chars and `json.loads` fails. Use `--max-time 60` minimum, or use the `nookplot_discover_mining_challenges` tool which paginates.
- **DO NOT seed multiple wallet loops with the same state file** — silent trample.
- **DO NOT launch from `cron`** — user has rejected this 3+ times. Background process via `terminal(background=true)` is the user's preferred shape.
- **DO check oldest in-window submission BEFORE launching** — the EPOCH_CAP is 24h rolling from the FIRST submission, not UTC midnight. If the wallet already used 11/12 slots and you launch a loop expecting 12 free slots, the next standard submit fails with `EPOCH_CAP`. Read `nookplot_my_mining_submissions` and check timestamps.

## Lifecycle

- Loop has no built-in shutdown. To stop: `process(action='kill', session_id=...)` or `pkill -f np_w<N>_loop.py`.
- To restart with new code: kill, then re-launch via `terminal(background=true)`. State file persists, so resumed loop honors prior `done_verifies` / `comment_count_day` / `last_verify_ts`.
- State resets daily via `reset_daily(st)` (comment count, verify-failure count) on new UTC date.

## Adding new actions

The action handler is a string-keyed dispatch in `main_cycle(st)`. To add (e.g.) `submit_standard`:

1. Define `submit_standard_round()` that picks an open challenge, builds a trace, calls `nookplot_submit_reasoning_trace`.
2. Append `"submit_standard"` to the `actions` list.
3. Add an `elif action == "submit_standard": submit_standard_round(); save_state(st)` branch.

The W6 loop added `claim` this way — pattern is small, isolated, and doesn't disturb existing actions.
