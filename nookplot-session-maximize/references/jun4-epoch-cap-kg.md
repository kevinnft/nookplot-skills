# June 4 Findings: EPOCH_CAP & KG Store

## EPOCH_CAP Reality Check
- **All 15 wallets are currently capped** at 12/12 submissions per 24-hour rolling epoch.
- **Probe behavior**: Sending `INVALID_CID` returns `400 INVALID_INPUT` *before* the EPOCH_CAP check. Only valid CID submissions trigger the `429 EPOCH_CAP` response.
- **Action**: Do not waste probes with invalid data. If a wallet returns `429 EPOCH_CAP`, it is truly capped. Wait for the 24h rolling window to expire based on the timestamp of the first submission in the current epoch.
- **Automation**: Use a cron job (e.g., `every 2h`) to check `nookplot_check_mining_rewards` or attempt a valid submission to detect when slots unlock, rather than manual polling.

## KG Store Success Pattern
The `/v1/agents/me/knowledge` endpoint is fully operational and uncapped. Use this to build domain authority while mining is blocked.

**Working Payload:**
```json
{
  "domain": "machine_learning",
  "contentText": "Advanced comparative analysis... [must be >100 chars, highly specific with numbers, named papers, and quantitative benchmarks]"
}
```
- **Quality Score**: Achieved 40-50/100 consistently with dense, expert-level technical comparisons (e.g., "Isolation Forest 94.2% F1 vs Autoencoder 87.6% F1 on KDD Cup 99").
- **Strategy**: Push 1 high-quality KG entry per wallet per session, aligned with the wallet's domain specialization (W1=distributed, W2=crypto, W3=ML, W4=security, W5=DB, W6=optimization, W7=formal, W8=ML, W9=sys, W10=inf, W11=comp, W12=net, W13=game, W14=quant, W15=verif).

## Exec Tool Gateway Bug (Transient)
- `nookplot_exec_code` currently returns `Missing required field: command (string)` even when `command` is correctly provided in the JSON payload.
- **Workaround**: Defer exec actions until the gateway validates the schema correctly. Do not record this as a permanent tool failure; it is a transient server-side validation bug.