#!/usr/bin/env python3
"""
verify_onchain_reward.py — verify claim landed on Base, classify outflows.

Usage:
    python verify_onchain_reward.py W4 W5 W6
    python verify_onchain_reward.py --all
    python verify_onchain_reward.py 0xdbAFE90B27F431EBC7660765925961af6570D9F2

For each wallet/address, prints:
  - current on-chain NOOK balance (direct Base RPC eth_call, no cache)
  - last 5 NOOK transfers (IN/OUT, counterparty, age, tx hash)
  - sink classification for OUT destinations (PoolManager / consolidator / external)
  - red flag if sink not in our cluster

Verifies "reward arrived" claims against the source of truth (Base mainnet).
Pairs with references/reward-claimed-but-missing-debug.md.
"""
from __future__ import annotations
import json, sys, subprocess, argparse
from datetime import datetime, timezone
from pathlib import Path

NOOK = "0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3"
DISTRIBUTOR = "0x3632428A".lower()  # Nookplot reward distributor prefix
RPC = "https://mainnet.base.org"
BLOCKSCOUT = "https://base.blockscout.com/api/v2"

KNOWN_SINKS = {
    "0xREDACTED_WALLET_40CHARS": ("Uniswap V4 PoolManager", "SOLD to ETH/USDC"),
    "0xREDACTED_WALLET_40CHARS": ("Consolidator EOA", "cluster sweep target"),
    "0xREDACTED_WALLET_40CHARS": ("Final sink EOA", "terminal cluster destination"),
}

WALLETS_FILE = Path.home() / ".hermes" / "nookplot_wallets.json"


def load_wallets() -> dict:
    try:
        return json.loads(WALLETS_FILE.read_text())
    except Exception:
        return {}


def rpc_balance(addr: str) -> float:
    data = "0x70a08231" + addr.lower().replace("0x", "").zfill(64)
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "eth_call",
        "params": [{"to": NOOK, "data": data}, "latest"],
    })
    r = subprocess.run(
        ["curl", "-sS", "-X", "POST", RPC,
         "-H", "Content-Type: application/json", "-d", payload],
        capture_output=True, text=True, timeout=20,
    )
    try:
        return int(json.loads(r.stdout)["result"], 16) / 1e18
    except Exception:
        return -1.0


def transfers(addr: str) -> list[dict]:
    url = f"{BLOCKSCOUT}/addresses/{addr}/token-transfers?type=ERC-20&token={NOOK}"
    r = subprocess.run(["curl", "-sS", url], capture_output=True, text=True, timeout=20)
    try:
        return json.loads(r.stdout).get("items", [])
    except Exception:
        return []


def classify_sink(addr: str, our_addrs: set[str]) -> str:
    a = addr.lower()
    if a in our_addrs:
        return "OUR cluster wallet (benign sweep)"
    if a in KNOWN_SINKS:
        return f"{KNOWN_SINKS[a][0]} — {KNOWN_SINKS[a][1]}"
    return "EXTERNAL (confirm with user — possible privkey leak)"


def report(label: str, addr: str, our_addrs: set[str]) -> None:
    print(f"\n=== {label} {addr} ===")
    bal = rpc_balance(addr)
    print(f"  on-chain NOOK balance (Base RPC): {bal:,.4f}")

    txs = transfers(addr)
    if not txs:
        print("  no NOOK transfers found")
        return

    now = datetime.now(timezone.utc)
    for tx in txs[:5]:
        ts = tx.get("timestamp", "")
        try:
            tx_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            age = (now - tx_time).total_seconds() / 60
            age_s = f"{age:>6.1f}m ago"
        except Exception:
            age_s = "?"
        val = float(tx.get("total", {}).get("value", "0")) / 1e18
        from_a = tx.get("from", {}).get("hash", "?").lower()
        to_a = tx.get("to", {}).get("hash", "?").lower()
        h = tx.get("transaction_hash", "?")[:18]
        if to_a == addr.lower():
            kind = "IN " if not from_a.startswith(DISTRIBUTOR) else "IN✓"
            tag = "from distributor" if from_a.startswith(DISTRIBUTOR) else "from " + from_a[:10]
            print(f"  {ts[:19]} {age_s} {kind} {val:>12,.2f} {tag}... tx={h}")
        else:
            sink = classify_sink(to_a, our_addrs)
            print(f"  {ts[:19]} {age_s} OUT {val:>12,.2f} → {to_a[:10]}... [{sink}] tx={h}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("targets", nargs="*", help="wallet keys (W1..W12) or 0x addresses")
    p.add_argument("--all", action="store_true", help="check all wallets in nookplot_wallets.json")
    args = p.parse_args()

    wallets = load_wallets()
    our_addrs = {w["addr"].lower() for w in wallets.values() if "addr" in w}

    targets: list[tuple[str, str]] = []  # (label, addr)
    if args.all:
        for k in sorted(wallets.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 999):
            targets.append((f"{k} {wallets[k].get('displayName','?')}", wallets[k]["addr"]))
    else:
        for t in args.targets:
            if t.startswith("0x"):
                targets.append((t[:10] + "...", t))
            elif t in wallets:
                targets.append((f"{t} {wallets[t].get('displayName','?')}", wallets[t]["addr"]))
            else:
                print(f"unknown target: {t}", file=sys.stderr)

    if not targets:
        print("no targets — pass W1..W12 keys, 0x addresses, or --all")
        return 1

    print(f"=== Base mainnet snapshot {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} ===")
    for label, addr in targets:
        report(label, addr, our_addrs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
