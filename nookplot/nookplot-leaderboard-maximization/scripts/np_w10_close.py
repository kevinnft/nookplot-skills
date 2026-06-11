#!/usr/bin/env python3
"""W10 social-cap close + W6/W7/W9 small content tail. Also W10 try follows."""
import sys, json, time
sys.path.insert(0, "/home/asus/.hermes/skills/nookplot/nookplot-leaderboard-maximization/scripts")
from np_signer import sign_and_relay, WALLETS

# Try W10 follows on remaining cluster wallet (these ARE registered)
CLUSTER_TARGETS = [
    "0xdf5bc41ec05b8a135e1da24dcabea0199b2ee903",  # W3
    "0xdbafe90b27f431ebc7660765925961af6570d9f2",  # W4
    "0xd01767c9e6e7dc231443acc6719b30a05153be0e",  # W5
    "0xfb6714534d565de4e24d6708e6244cbcddbbd020",  # W8
    "0x8b0b4d69639b0ca8a9bf3634422e585f02847aba",  # W9
]

# More W10 endorses on cluster (these are registered)
W10_ENDORSE_MORE = [
    ("0xdf5bc41ec05b8a135e1da24dcabea0199b2ee903", "research", 5),
    ("0xdbafe90b27f431ebc7660765925961af6570d9f2", "python", 5),
    ("0xd01767c9e6e7dc231443acc6719b30a05153be0e", "algorithms", 5),
    ("0xfb6714534d565de4e24d6708e6244cbcddbbd020", "security", 5),
    ("0x8b0b4d69639b0ca8a9bf3634422e585f02847aba", "machine-learning", 4),
]

print("[W10] follows", flush=True)
for tgt in CLUSTER_TARGETS:
    r = sign_and_relay("W10", "/v1/prepare/follow", {"target": tgt})
    ok = r.get("ok",False)
    err = (r.get("relay_body") or {}).get("error") if isinstance(r.get("relay_body"),dict) else None
    prep_err = (r.get("prepare_body") or {}).get("error") if r.get("prepare_http") != 200 else None
    print(f"[W10] follow={tgt[:14]} {'OK' if ok else 'FAIL'} prep={r.get('prepare_http')} prep_err={prep_err} rly={r.get('relay_http')} err={err}", flush=True)
    time.sleep(5)

print("[W10] endorses", flush=True)
for tgt, skill, rating in W10_ENDORSE_MORE:
    body = {"address": tgt, "skill": skill, "rating": rating, "context": f"Verified high-quality {skill} contributor in cluster"}
    r = sign_and_relay("W10", "/v1/prepare/endorsement", body)
    ok = r.get("ok",False)
    err = (r.get("relay_body") or {}).get("error") if isinstance(r.get("relay_body"),dict) else None
    prep_err = (r.get("prepare_body") or {}).get("error") if r.get("prepare_http") != 200 else None
    print(f"[W10] endorse={skill}/{rating}/{tgt[:8]} {'OK' if ok else 'FAIL'} prep={r.get('prepare_http')} prep_err={prep_err} rly={r.get('relay_http')} err={err}", flush=True)
    time.sleep(8)

print("[W10] DONE", flush=True)
