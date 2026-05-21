# Response Format Preferences

## Status Queries vs Count Queries

**Status queries** ("sudah maksimal?", "cek ulang", "kapan bisa lanjut?") expect:
1. Per-dimension table: caps hit vs open
2. Each ceiling's unblock ETA with computed UTC+WIB+relative-hours timestamps
3. Concrete polling intervals

Template: `sudah-maksimal-eta-reporting.md`

**Count queries** ("berapa wallet", "ada berapa X", "cek ada berapa") expect:
- **Direct answer only** — no full audit, no dimension tables, no ETA analysis
- User preference (May 2026): count queries are informational lookups, not status checks
- Right shape: "12 wallets" or "50 open submissions"
- Wrong shape: launching full audit script, per-wallet breakdown, ceiling analysis

## Detection Pattern

```python
# Count query signals
count_keywords = ["berapa", "ada berapa", "cek ada berapa", "how many"]
status_keywords = ["sudah maksimal", "cek ulang", "kapan bisa", "sudah mantap"]

if any(k in user_msg.lower() for k in count_keywords):
    # Direct answer path
    return simple_count()
elif any(k in user_msg.lower() for k in status_keywords):
    # Full audit path
    return comprehensive_status_with_eta()
```

## Rationale

User frustration pattern: asking "cek ada berapa wallet" and receiving a 20-line audit script with per-wallet breakdowns when they just wanted "12 wallets". Count queries are quick lookups; status queries are operational audits. Treat them differently.
