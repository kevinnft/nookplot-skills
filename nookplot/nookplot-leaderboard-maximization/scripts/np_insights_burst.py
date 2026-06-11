#!/usr/bin/env python3
"""Publish 1 insight per wallet across cluster via REST direct.

USAGE
    Edit INSIGHTS dict (one entry per wallet, ≥200-char body).
    python3 np_insights_burst.py

WHY THIS SCRIPT
    publish_insight via /v1/actions/execute SILENTLY STRIPS the title field
    (returns "title is required" even when title is present). Direct POST
    to /v1/insights with snake_case `strategy_type` is the only working path.
    See references/reward-channel-api-quirks.md for full table.

CONTRACT
    POST https://gateway.nookplot.com/v1/insights
    Headers: Authorization: Bearer <apiKey>, Content-Type: application/json
    Body: {title, body, strategy_type:"general", tags:[...]}

    strategy_type accepted values on REST: "general" only.
    "observation" and "recommendation" return Invalid strategy_type.
    (MCP tool nookplot_publish_insight uses different camelCase contract.)

RATE LIMITS
    No documented daily cap. Short-window 429 on rapid bursts (~5 parallel OK,
    >5 risk 429). Retry with 30-60s cooldown clears.
"""

import json
import random
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

WALLETS_PATH = Path.home() / ".hermes" / "nookplot_wallets.json"
GATEWAY = "https://gateway.nookplot.com"

# Customize per burst — title must be distinct per wallet to avoid 409 dedupe.
# Body ≥200 chars substantive markdown.
INSIGHTS: dict[str, tuple[str, str]] = {
    # "W2": ("Title here", "Body markdown here..."),
    # "W3": ("...", "..."),
}


def load_wallets() -> dict:
    return json.loads(WALLETS_PATH.read_text())


def publish(wallets: dict, wkey: str, title: str, body: str) -> tuple[str, str, str]:
    w = wallets[wkey]
    payload = {
        "title": title,
        "body": body,
        "strategy_type": "general",
        "tags": ["nookplot-mining", wkey.lower()],
    }
    r = subprocess.run(
        [
            "curl", "-s", "-X", "POST", f"{GATEWAY}/v1/insights",
            "-H", f"Authorization: Bearer {w['apiKey']}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload),
        ],
        capture_output=True, text=True, timeout=30,
    )
    try:
        resp = json.loads(r.stdout)
        if "insight" in resp:
            return wkey, "OK", resp["insight"].get("id", "")
        if "error" in resp:
            return wkey, "ERR", str(resp.get("error", "?"))
        return wkey, "UNK", str(resp)[:200]
    except Exception as e:
        return wkey, "EXC", f"{e}: {r.stdout[:200]}"


def burst(wallets: dict, plan: dict, max_workers: int = 5) -> list[tuple[str, str, str]]:
    """Wave 1: parallel up to max_workers across wallets."""
    def worker(wkey):
        title, body = plan[wkey]
        time.sleep(random.uniform(0.2, 1.5))  # spread to dodge short-window
        return publish(wallets, wkey, title, body)

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = [ex.submit(worker, k) for k in plan.keys()]
        for f in as_completed(futs):
            r = f.result()
            results.append(r)
            print(f"[{r[0]}] {r[1]} {r[2]}")
    return results


def retry_429(wallets: dict, plan: dict, results: list, cooldown_sec: int = 60,
              max_attempts: int = 3) -> list:
    """Wave 2: serial retry of 429s with longer cooldown."""
    failed = [r[0] for r in results if r[1] != "OK" and "Too many" in str(r[2])]
    print(f"\nRetrying {len(failed)} 429s serially with {cooldown_sec}s cooldown...")
    new_results = list(results)
    for wkey in failed:
        title, body = plan[wkey]
        for attempt in range(max_attempts):
            r = publish(wallets, wkey, title, body)
            if r[1] == "OK":
                # replace failed entry
                new_results = [x for x in new_results if x[0] != wkey] + [r]
                print(f"[{wkey}] OK on attempt {attempt+1}: {r[2]}")
                break
            print(f"  [{wkey} attempt {attempt+1}] {r[1]} {r[2]}")
            time.sleep(cooldown_sec)
    return new_results


def main():
    if not INSIGHTS:
        print("Edit INSIGHTS dict in this script before running.")
        return
    wallets = load_wallets()
    results = burst(wallets, INSIGHTS, max_workers=5)
    results = retry_429(wallets, INSIGHTS, results)
    ok = sum(1 for r in results if r[1] == "OK")
    print(f"\n=== SUMMARY ===\nOK {ok}/{len(INSIGHTS)}")
    fails = [r for r in results if r[1] != "OK"]
    if fails:
        print(f"FAIL: {fails}")


if __name__ == "__main__":
    main()
