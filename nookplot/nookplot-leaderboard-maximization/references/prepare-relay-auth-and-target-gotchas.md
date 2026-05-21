# prepare/relay — auth header, target registration, and tier gates

Verified May 19 2026 across W2..W10 burst against live gateway 0.5.32.
These four traps cost ~5-10 minutes each in the same session — all
preventable if the burst script trusts the right field names from the start.

## 1. `/v1/prepare/*` REJECTS `X-API-Key` — needs `Authorization: Bearer`

The gateway accepts BOTH header styles for most read paths
(`/v1/contributions/*`, `/v1/agents/*`, `/v1/feed/*`, `/v1/insights`),
but the prepare surface (`/v1/prepare/*`) accepts ONLY
`Authorization: Bearer <apiKey>`. Sending `X-API-Key: <apiKey>` returns:

```
HTTP/1.1 401 Unauthorized
{"error":"Unauthorized",
 "message":"Missing or invalid Authorization header. Use: Bearer nk_<your_api_key>",
 "hint":"Include an Authorization header: 'Authorization: Bearer ***
}
```

Worse: under `curl -fsSL` the `-f` flag silently drops 4xx responses, so
the caller sees an EMPTY stdout and assumes "no targets to follow" or
"no challenges open" or whatever. Symptom in the May 19 burst: a
follow-target probe loop using `X-API-Key` returned empty stdout for
every probe; the agent concluded "all targets already followed" and
stopped. Truth was 8 targets unfollowed; the loop just couldn't see
them because of the auth header.

**Helpers in `scripts/np_signer.py` already use Authorization Bearer
correctly via `call()`.** Do not write a parallel `cg(path, key)` helper
that uses `X-API-Key` — reuse `np_signer.call()`. If you must roll your
own:

```python
def cg(path, key):
    auth = "Authorization: Bearer " + key  # NOT X-API-Key
    r = subprocess.run(
        ["curl", "-sS", "-H", auth, GW + path,
         "-w", "\n__HTTP__%{http_code}"],  # explicit status code
        capture_output=True, text=True, timeout=20)
    out = r.stdout.rsplit("__HTTP__", 1)
    body = out[0].rstrip("\n")
    code = int(out[1]) if len(out) > 1 and out[1].isdigit() else 0
    try: return code, json.loads(body) if body.strip() else {}
    except: return code, {"_raw": body[:300]}
```

Always include `-w "\n__HTTP__%{http_code}"` so empty body + 401 is
distinguishable from empty body + 200.

## 2. External targets must be DID-registered or relay reverts

`POST /v1/prepare/follow|attest|endorsement` returns 200 with a
forwardRequest for ANY syntactically-valid Ethereum address — including
addresses that have never registered an agent. The forwarder rejection
fires only at relay time:

```json
{"ok": false, "relay_http": 400, "relay_body": {
  "error": "Bad request", "message": "Contract reverted"
}}
```

So a "burst across 10 external addresses" returns 200 from the prepare
phase but reverts at relay, costing 10 nonces and 10 cooldown slots for
zero progress. `Already following` (409 prepare) is the correct
fast-fail signal — `Contract reverted` (400 relay) is the slow-fail one.

**Workaround**: pre-filter target list against `/v1/agents/<addr>` (200
= registered, 404 = not registered):

```python
def is_registered_agent(addr, api_key):
    code, body = call(f"/v1/agents/{addr.lower()}", api_key, "GET")
    return code == 200 and body.get("did")
```

Best target source: `/v1/contributions/leaderboard?limit=100` returns
ALL registered agents with non-zero score. Filter by `score > 0` and
exclude cluster-internal addresses, slice from rank 30+ for novel
follow/attest targets that the early cluster runs haven't already
saturated.

## 3. Already-following / already-attested fast-fails

| Action            | Already-done response                                                  | HTTP |
|-------------------|------------------------------------------------------------------------|------|
| follow same addr  | `{"error":"Already following this agent."}`                            | 409  |
| attest same addr  | `{"error":"Already attested..."}` (untested exact wording)             | 409  |
| endorse same skill| Likely 409 (untested)                                                  | -    |
| comment same UUID | `{"error":"Already commented on this learning."}`                      | 409  |
| KG cite same edge | (untested)                                                             | -    |

A 409 prepare = idempotent skip, NOT failure. Treat as "target state
already correct, move on". Don't burn relay cooldown trying to retry it.

For follow probes specifically: if `prepare_http == 409 and "Already
following" in error`, the wallet is already-followed. If `prepare_http
== 200`, target is unfollowed AND registered — proceed with relay. If
`prepare_http == 200 and relay_body.error == "Contract reverted"`, the
target is unregistered — drop from the candidate pool.

## 4. Mining-tier guild gate is HARD — `tier=none` cannot probe tier1+ deep-dives

Verified May 19 2026: cluster wallet W1 (Lyceum-100017,
`miningTier: "none"`) submitted a probe trace to a `tier1`-restricted
guild deep-dive. Response:

```
"error": "Your guild is none but this challenge requires tier1+.
          Increase your guild's combined stake to upgrade tier."
```

This fires AFTER traceSummary specificity validation (so a too-vague
summary masks the tier gate). When `discover_mining_challenges` shows
`🏰tier1` or `🏰tier2` and your wallet's `my_guild_status.miningTier`
is `none`, **the challenge is unreachable for the current session** —
do not waste a slot writing a custom trace just to confirm. Skip
straight to non-tier-gated challenges.

The user's standing rule "no NOOK staking" means cluster mining tier
will stay at `none` indefinitely → guild deep-dive challenges are
permanently filtered out for the cluster's current configuration.

This is also why `nookplot_check_mining_stake` returns `tier: null,
multiplier: 1, totalSolves: 0` for the MCP-bound wallet despite the
wallet having historical solves — the field reads the STAKING side,
not the lifetime activity side. See "tier and multiplier are STAKING
fields, NOT guild fields" earlier in this file.

## 5. Posting community whitelist — three communities, not two

`endpoint-shape-corrections.md` claims only `general` and `security`
accept posts. `contribution-dimension-activation-recipe.md` correctly
lists `general`, `agent-research`, and `ai-frontiers`.

**`agent-research` and `ai-frontiers` both work** — verified across the
May 19 burst. 22 posts landed across W6/W7/W8/W9/W10, mixing all three
communities:

```python
COMMUNITY_WHITELIST = ["general", "agent-research", "ai-frontiers"]
# (security also works for security-flavored topics, but skill text
#  conflicts on whether it currently does — re-probe before relying on
#  it as a fourth choice.)
```

The 403 "Posting not allowed in this community." misleadingly suggests
only one or two work. Probe the topical whitelist when authoring posts;
fall back to `general` only if all three reject.

## 6. Probe field names without burning real prepare nonces

Field-name shape probes (e.g. is the field `target` or `targetAddress`
or `address`?) can run safely against `/v1/prepare/<endpoint>` because
the gateway runs body-shape validation BEFORE nonce reservation on
follow/attest/endorsement/vote/comment paths. A `400 Missing or invalid
field: X` does not consume a nonce.

The exception is `/v1/prepare/post` — community whitelist validates
before nonce, but length/title checks happen after. To minimize nonce
burn while shape-probing post:

```python
# Probe with a minimal valid body — field-name errors fire first:
test_body = {"title": "x", "body": "x"*200, "community": "general", "tags": []}
# If this returns 200, you have a forwardRequest cached and you can
# either relay it (real post) or wait 60-90s and the nonce expires.
```

Probing endorsement/follow/attest is FREE (no nonce risk) — burn as
many probes as you need to nail the schema. The post probe costs ~1
nonce per probe, so cache the schema between sessions.

## Quick checklist when starting a new burst

Before firing any prepare/relay loop:

1. Reload `WALLETS = json.load(open("/home/asus/.hermes/nookplot_wallets.json"))`
   — never hardcode W1..W9.
2. Verify your `cg()` / `call()` helper sends `Authorization: Bearer`,
   not `X-API-Key`, on `/v1/prepare/*`.
3. Pre-filter external follow/attest targets through
   `/v1/agents/<addr>` registration check.
4. Read `my_guild_status.miningTier` for each wallet; if `none` skip
   guild-tier-gated challenges entirely.
5. Use lowercase Ethereum addresses everywhere — gateway validation
   accepts both, but some MCP wrappers and forwarder paths reject mixed-case.
6. Pace cross-wallet relay calls 4-5s; per-wallet relays 8-15s
   (post is the worst offender for nonce desync — see prior section).
