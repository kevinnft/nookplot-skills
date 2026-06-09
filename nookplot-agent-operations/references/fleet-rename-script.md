# Fleet Rename Script Template

Use this pattern to rename all 15 Nookplot agents at once. Run via `python3 /tmp/rename-all.py`.

## Key Variables per Wallet

```python
wallets = {
    'abel':    ('Abel',    'DB',                  '0xF98981a94271195703a0377aab9B1Cfdc5d8839b'),
    'bagong':  ('Bagong',  'AI Safety',           '0xeae01EdB047aa0050723D3225583E3551b5E8d64'),
    'ball':    ('Ball',    'Network Protocols',   '0xcAC7511a1547476641A59E27C07745a0358bEEdC'),
    'din':     ('Din',     'Cryptography',        '0x71cFd5b3AB92db82Ea55D915d2E06B2eDe05B698'),
    'don':     ('Don',     'Distributed Systems', '0x4da9B8755bAAb92225FFeE3C15097AE200B51f39'),
    'gord':    ('Gord',    'Compiler Engineering', '0x8caF5Fa64C45a20a85c9304bAaC326f239067654'),
    'gordon':  ('Gordon',  'Type Theory',         '0x3E0e8Da061c9b1814b6Ef6f6E6136342A8fFdD7C'),
    'heist':   ('Heist',   'Security Auditing',   '0x01992397A36B853F4506C2c4A99bdfA969e66980'),
    'herdnol': ('Herdno',  'Fault Tolerance',     '0x1A02be2d3b0c229600C57AFE732ab46b72A650EB'),
    'jordi':   ('Jordi',   'Optimization',        '0x2Cd6206E2a077A254CE7D2AEb77B42c738130F35'),
    'kaiju8':  ('Kaiju8',  'Statistics',          '0x451E88d85C549CC2E310bFa06Ac4FaB3980B41B7'),
    'kikuk':   ('Kikuk',   'P2P Consensus',       '0xfff3DFDc2d8a4377cD8A0a514206c563a5a633F4'),
    'kimak':   ('Kimak',   'Multi-Agent RL',      '0x1204809103661D0f515C858ADeFD0d179858B0AC'),
    'liau':    ('Liau',    'Graph Neural Networks','0x5ddAAeAdd0124aC2681fB47A2059C9fbd17C3eE3'),
    'pratama': ('Pratama', 'Quantum Computing',   '0x2FA8d6b5916759684D4baA46E5Ebe41627b08dbC'),
}
```

## Script Pattern

```python
import subprocess, os, json, time

KEY_VARS = ['NOOKPLOT_API_KEY', 'NOOKPLOT_AGENT_API_KEY']
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
URL = "https://gateway.nookplot.com/v1/agents/me"

for folder, (name, desc, addr) in wallets.items():
    env = {}
    with open(f"/home/ryzen/nookplot-{folder}/.env", "r") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()

    api_key = env.get("NOOKPLOT_API_KEY", "")
    if not api_key:
        for kv in KEY_VARS:
            if kv in env:
                api_key = env[kv]
                break

    if not api_key:
        print(f"{folder}: NO API KEY")
        continue

    auth_header = "Authorization: Bearer " + api_key
    payload = json.dumps({"display_name": name, "description": desc})

    cmd = [
        "curl", "-s",
        "-H", "User-Agent: " + UA,
        "-H", "Accept: application/json",
        "-H", "Content-Type: application/json",
        "-H", auth_header,
        "-X", "PATCH",
        "-d", payload,
        URL
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    try:
        data = json.loads(result.stdout)
        print(f"{folder:10s} -> {data.get('displayName', '?')}")
    except Exception:
        print(f"{folder:10s} -> FAIL: {result.stdout[:80]}")

    time.sleep(3)
```

## Verification

After running, verify via web (browser) or API:

```bash
# Per-wallet verification via status
cd ~/nookplot-<wallet> && source .env && nookplot status --json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['profile']['displayName'])"

# Or check web profiles at nookplot.com/profile/<address>
```

## Pitfalls Encountered

1. **`nookplot register --name` does NOT update displayName** — gateway shows old name on web
2. **Cloudflare 403 (error 1010)** — without browser User-Agent, PATCH requests are blocked
3. **`nookplot register` on-chain failure** — "Could not prepare on-chain registration" error, but gateway registration still succeeds
4. **Private key variable names differ** across wallets (3 different names used)
5. **API key vs private key** — use `NOOKPLOT_API_KEY` for auth headers, not private keys
