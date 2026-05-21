# Quick-Reply Rules (Non-Negotiable)

These override ANY "maksimal" / "audit" / "sudah maksimal" trigger when the
user's actual prompt is a simple query.

## Response Shape Table

| Prompt Shape | Correct Response |
|---|---|
| "berapa wallet" / "ada berapa X" / "cek berapa" | Direct answer, no audit, no table, no "Gas sekarang?" |
| "kondisi W7" / "status wallet" bare | 1-3 line summary. Full audit only if user asks "sudah maksimal?" |
| "claim reward" bare | Status-check only, NOT execute. Report claimable balance and stop. |

## Why This Matters

When user asks "hanya cek ada berapa wallet nookplot", they get a one-liner
answer (12). A full audit + "Gas sekarang?" is noise — it forces them to
dismiss 10 lines they didn't ask for.

Full systematic audit (per-wallet breakdown, all channels, ETAs per ceiling,
"Gas sekarang?") is reserved for explicit requests:
- "sudah maksimal?" / "sudah mantap?"
- "cek ulang" / "kapan bisa lanjut?"
- "audit lengkap" / any variant requesting systematic completeness

## Decision Flow

```
user prompt → match quick-reply pattern?
  → YES: direct answer, STOP. No audit, no tables, no follow-up question.
  → NO:  load full audit flow (hard-rules → reward-channels → bounty-sweep → ...)
```

When in doubt, ask once: "Report doang atau mau action juga?" Default to
report-only.

## Trigger Keywords for Quick-Reply Mode

- berapa, ada berapa, jumlah, count
- hanya cek, quick check, just check
- just wants the number / count (no audit implied)