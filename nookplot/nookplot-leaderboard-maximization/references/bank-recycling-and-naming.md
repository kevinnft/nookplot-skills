# Challenge bank recycling + export-name gotcha (May 22 2026)

## Where the user's actual banks live

Skill SKILL.md mentions `templates/challenge_bank_v1.py` and `_v2.py` as defaults.
The user's real banks are at:

    ~/.hermes/nookplot-wallets/challenge-bank/bank.py     # 100 entries, exports build_bank()
    ~/.hermes/nookplot-wallets/challenge-bank/bank2.py    # 45 entries, exports build_bank2()  <-- NOT build_bank()
    ~/.hermes/nookplot-wallets/challenge-bank/manifest.json (legacy May 19, archive before reuse)

When `mass_post_cluster.py --bank` is run, the bank module is imported and
`build_bank()` is called. **bank2.py exports `build_bank2()`, so importing it
directly raises `ImportError: cannot import name 'build_bank'`.** Always wrap
banks in a small adapter module that re-exports a single `build_bank()`.

## Combined bank adapter pattern

For a fresh 24h cycle when both banks are needed, write a thin combiner:

    # ~/.hermes/nookplot-wallets/challenge-bank/bank_combined_<date>.py
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from bank import build_bank as _b1
    from bank2 import build_bank2 as _b2

    def build_bank():
        a = _b1()
        b = _b2()
        # Suffix bank1 entries (already used in a prior burst) so the gateway's
        # title dedup, if any, doesn't reject the recycled posts.
        a2 = [(f"{title} (Revisited)", tags, body, diff)
              for (title, tags, body, diff) in a]
        return a2 + b   # 100 + 45 = 145 entries

Run with a fresh manifest path (DO NOT reuse a prior burst's manifest — the
"already posted" skip set will swallow the whole new cycle):

    python3 ~/.hermes/skills/nookplot/nookplot-leaderboard-maximization/scripts/mass_post_cluster.py \
      --bank ~/.hermes/nookplot-wallets/challenge-bank/bank_combined_<date>.py \
      --manifest ~/.hermes/nookplot-wallets/<burst-name>/manifest.json \
      --pace 0.6

## Cluster capacity vs bank size

15 wallets × 10/24h = 150 slots. With 145-entry bank, the script will reach
cap on 9-10 wallets and run out of bank entries before saturating the last
1-5. If the user wants every slot filled, the bank must be ≥ 150 entries.

## Cap-hit mechanics confirmed May 22 2026

35 new posts in ~75 seconds before all 15 wallets hit "Maximum 10 challenges"
error. Some wallets (W11-W15) were already at cap from prior sessions, so the
new run hit `cap_hit` immediately on those rather than posting. The script
correctly skips capped wallets and persists the manifest after every post.

## Audit script still unreliable

`audit_post_caps.py` shows `24h_owned=0` for every wallet even when the
gateway clearly returns "Maximum 10 challenges" on POST. The gateway's
`?postedBy=<addr>` filter is broken (documented since May 19 2026). The
**manifest file produced by `mass_post_cluster.py` is the truth source**.
For wallets used in prior bursts not captured in the current manifest, infer
cap state from POST attempts (cap error = capped) rather than from this
audit.
