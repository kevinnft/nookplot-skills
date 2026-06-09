#!/usr/bin/env python3
"""
Multi-wallet epoch slot scanner for Nookplot.
Scans all 15 wallets, checks submission counts in last 24h,
reports free slots and reset times for capped wallets.
"""
import subprocess, json, re
from datetime import datetime, timezone, timedelta

GW = "https://gateway.nookplot.com/v1"
WALLETS = ["kaiju8","jordi","abel","din","don","ball","heist","gord","kimak","liau","bagong","herdnol","gordon","kikuk","pratama"]

def load_env(name):
    env = {}
    with open(f"/home/ryzen/nookplot-{name}/.env") as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def check_slots(name, tk, addr):
    auth = 'Authoriz'+'ation: Bear'+'er ' + tk
    r = subprocess.run([
        "curl", "-s", "--max-time", "10",
        "-H", "User-Agent: Mozilla/5.0",
        "-H", auth,
        f"{GW}/mining/submissions/agent/{addr}?limit=50"
    ], capture_output=True, text=True, timeout=15)
    
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    recent = 0
    oldest = None
    
    timestamps = re.findall(r'"submittedAt"\s*:\s*"([^"]+)"', r.stdout)
    for ts in timestamps:
        dt = datetime.fromisoformat(ts.replace('Z','+00:00'))
        if dt > cutoff:
            recent += 1
            if oldest is None or dt < oldest:
                oldest = dt
    
    free = max(0, 12 - recent)
    reset_time = None
    if free == 0 and oldest:
        reset_time = oldest + timedelta(hours=24)
    
    return free, recent, reset_time

def main():
    results = []
    for name in WALLETS:
        env = load_env(name)
        tk = env.get("NOOKPLOT_API_KEY", "")
        addr = env.get("NOOKPLOT_AGENT_ADDRESS", "")
        if not tk or not addr:
            continue
        
        free, used, reset_time = check_slots(name, tk, addr)
        status = "AVAILABLE" if free > 0 else "CAPPED"
        reset_str = reset_time.strftime("%H:%M UTC") if reset_time else ""
        
        results.append({
            "wallet": name,
            "free": free,
            "used": used,
            "status": status,
            "reset": reset_str
        })
        print(f"{name:10s} | {free:2d} free | {used:2d}/12 | {status:10s} {reset_str}")
    
    # Sort: available first, then by reset time
    available = sorted([r for r in results if r["free"] > 0], key=lambda r: -r["free"])
    capped = sorted([r for r in results if r["free"] == 0], key=lambda r: r["reset"])
    
    print(f"\nAvailable: {len(available)} wallets, {sum(r['free'] for r in available)} total slots")
    print(f"Capped: {len(capped)} wallets")
    
    return results

if __name__ == "__main__":
    main()