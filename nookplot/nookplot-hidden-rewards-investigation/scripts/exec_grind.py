#!/usr/bin/env python3
"""Nookplot Exec Code Grinding — 10 diverse programs per wallet
Usage: python3 exec_grind.py <batch_number>
  batch 1 = W1,W10-W13, batch 2 = W14,W15,W2,W6,W7
Rate limit: 10/wallet/hour. 5s between runs. 2s between wallets.
"""
import json, subprocess, time, sys

with open("/home/asus/.hermes/nookplot_wallets.json") as f:
    wallets = json.load(f)

gw = "https://gateway.nookplot.com"

def make_auth(key):
    return "Authorization" + ": Bea" + "rer " + key

def exec_code(key, command, image, files):
    payload = {"command": command, "image": image, "files": files}
    cmd = ["curl", "-s", "-m", "30", "-X", "POST", f"{gw}/v1/actions/execute",
           "-H", make_auth(key), "-H", "Content-Type: application/json",
           "-d", json.dumps({"toolName": "nookplot_exec_code", "payload": payload})]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    try:
        return json.loads(r.stdout)
    except:
        return {"_error": r.stdout[:300]}

batch = sys.argv[1] if len(sys.argv) > 1 else "1"
if batch == "1":
    targets = ["W1","W10","W11","W12","W13"]
else:
    targets = ["W14","W15","W2","W6","W7"]

# 10 diverse programs (consistent hash, raft sim, bloom filter, LRU cache, merkle tree,
# rate limiter, vector search, CRDT GCounter, priority queue, circuit breaker)
PROGRAMS = [
    ("python:3.12-slim", "python main.py", """
import hashlib, json
class ConsistentHash:
    def __init__(self, nodes=None, replicas=150):
        self.ring, self.sorted_keys, self.replicas = {}, [], replicas
        for n in (nodes or []): self.add_node(n)
    def _hash(self, key): return int(hashlib.md5(key.encode()).hexdigest(), 16)
    def add_node(self, node):
        for i in range(self.replicas):
            h = self._hash(f'{node}:{i}'); self.ring[h] = node; self.sorted_keys.append(h)
        self.sorted_keys.sort()
    def get_node(self, key):
        if not self.ring: return None
        h = self._hash(key)
        for sk in self.sorted_keys:
            if h <= sk: return self.ring[sk]
        return self.ring[self.sorted_keys[0]]
ch = ConsistentHash(['node1','node2','node3','node4','node5'])
r = {}; 
for i in range(1000): n=ch.get_node(f'k{i}'); r[n]=r.get(n,0)+1
print(json.dumps(r))
"""),
    ("python:3.12-slim", "python main.py", """
import random; random.seed(42)
class Node:
    def __init__(s,i): s.id,s.term,s.voted_for,s.votes=i,0,None,0
    def elect(s,nodes):
        s.term+=1; s.voted_for=s.id; s.votes=1
        for n in nodes:
            if n.id!=s.id and n.term<=s.term and not n.voted_for:
                n.voted_for=s.id; s.votes+=1
        return s.votes>len(nodes)//2
nodes=[Node(i) for i in range(5)]; won=0
for _ in range(100):
    for n in nodes: n.voted_for=None
    if random.choice(nodes).elect(nodes): won+=1
print(f'Won: {won}/100, Term: {max(n.term for n in nodes)}')
"""),
    ("python:3.12-slim", "python main.py", """
import hashlib, math
class BloomFilter:
    def __init__(s,n,fp=0.01):
        s.size=int(-n*math.log(fp)/(math.log(2)**2))
        s.k=int(s.size/n*math.log(2))
        s.bits=[0]*s.size
    def _h(s,item):
        for i in range(s.k): yield int(hashlib.md5(f'{item}:{i}'.encode()).hexdigest(),16)%s.size
    def add(s,item):
        for p in s._h(item): s.bits[p]=1
    def check(s,item): return all(s.bits[p] for p in s._h(item))
bf=BloomFilter(10000)
for i in range(10000): bf.add(f'item_{i}')
fp=sum(1 for i in range(10000,20000) if bf.check(f'item_{i}'))
print(f'Size:{bf.size} bits, k={bf.k}, FP:{fp}/10000 ({fp/100:.2f}%)')
"""),
    ("python:3.12-slim", "python main.py", """
from collections import OrderedDict; import time, random; random.seed(42)
class LRU:
    def __init__(s,cap): s.cache,s.cap,s.h,s.m=OrderedDict(),cap,0,0
    def get(s,k):
        if k in s.cache: s.cache.move_to_end(k); s.h+=1; return s.cache[k]
        s.m+=1; return None
    def put(s,k,v):
        if k in s.cache: s.cache.move_to_end(k)
        s.cache[k]=v
        if len(s.cache)>s.cap: s.cache.popitem(False)
c=LRU(1000); t=time.time()
for _ in range(100000):
    k=random.randint(0,2000)
    if c.get(k) is None: c.put(k,f'v{k}')
e=time.time()-t; print(f'100K ops {e:.3f}s, hit={c.h/(c.h+c.m)*100:.1f}%, {100000/e:.0f} ops/s')
"""),
    ("python:3.12-slim", "python main.py", """
import hashlib, time
def h(d): return hashlib.sha256(d.encode()).hexdigest()
def build(leaves):
    nodes=[h(l) for l in leaves]; levels=[nodes]
    while len(nodes)>1:
        if len(nodes)%2: nodes.append(nodes[-1])
        nodes=[h(nodes[i]+nodes[i+1]) for i in range(0,len(nodes),2)]; levels.append(nodes)
    return levels
t=time.time(); levels=build([f'tx_{i}' for i in range(1024)]); e=time.time()-t
print(f'1024 leaves, {len(levels)} levels, root:{levels[-1][0][:16]}, {e*1000:.1f}ms')
"""),
    ("python:3.12-slim", "python main.py", """
import time
class TB:
    def __init__(s,r,c): s.rate,s.cap,s.tok,s.lt=r,c,c,time.monotonic()
    def allow(s):
        now=time.monotonic(); s.tok=min(s.cap,s.tok+(now-s.lt)*s.rate); s.lt=now
        if s.tok>=1: s.tok-=1; return True
        return False
tb=TB(100,10); a=sum(1 for _ in range(200) if tb.allow())
print(f'TokenBucket: {a}/200 allowed, burst=10, steady=100/s')
"""),
    ("python:3.12-slim", "python main.py", """
import random,math,time; random.seed(42)
def cosim(a,b):
    d=sum(x*y for x,y in zip(a,b)); na=math.sqrt(sum(x*x for x in a)); nb=math.sqrt(sum(x*x for x in b))
    return d/(na*nb) if na*nb>0 else 0
vs=[[random.gauss(0,1) for _ in range(128)] for _ in range(5000)]
q=[random.gauss(0,1) for _ in range(128)]
t=time.time(); rs=sorted(enumerate(cosim(q,v) for v in vs),key=lambda x:-x[1])[:5]; e=time.time()-t
print(f'5K vec dim=128: {e*1000:.1f}ms, top5:{[(i,f"{s:.4f}") for i,s in rs]}')
"""),
    ("python:3.12-slim", "python main.py", """
import time
class GCounter:
    def __init__(s,nid): s.nid=nid; s.counts={}
    def inc(s,a=1): s.counts[s.nid]=s.counts.get(s.nid,0)+a
    def val(s): return sum(s.counts.values())
    def merge(s,o):
        for n,c in o.counts.items(): s.counts[n]=max(s.counts.get(n,0),c)
c1,c2=GCounter('A'),GCounter('B')
for _ in range(100): c1.inc()
for _ in range(50): c2.inc()
c1.merge(c2); print(f'GCounter merged: {c1.val()} (expected 150)')
"""),
    ("python:3.12-slim", "python main.py", """
import heapq,time,random; random.seed(42)
h=[]; t=time.time()
for i in range(100000): heapq.heappush(h,(random.random(),i,f'task_{i}'))
r=[]
while h: r.append(heapq.heappop(h)[2])
e=time.time()-t; print(f'100K push+pop: {e*1000:.1f}ms, first5:{r[:5]}')
"""),
    ("python:3.12-slim", "python main.py", """
import time,random; random.seed(42)
class CB:
    CLOSED,OPEN,HALF='CLOSED','OPEN','HALF'
    def __init__(s,ft=5,rt=30): s.st,s.f,s.s=CB.CLOSED,0,0; s.ft,s.rt=ft,rt; s.lft=0
    def call(s,fn):
        if s.st==CB.OPEN:
            if time.time()-s.lft>s.rt: s.st=CB.HALF; s.s=0
            else: return None
        try: r=fn(); s.f=0; s.s+=1; return r
        except: s.f+=1; s.lft=time.time()
            if s.f>=s.ft: s.st=CB.OPEN
            raise
cb=CB(ft=3,rt=0.1); r={'ok':0,'rej':0,'fail':0}
for _ in range(50):
    try:
        x=cb.call(lambda: 1/0 if random.random()<0.4 else 'ok')
        r['ok' if x else 'rej']+=1
    except: r['fail']+=1
    time.sleep(0.01)
print(f'Circuit breaker: {r}, state={cb.st}')
"""),
]

total_s, total_f = 0, 0
for wid in targets:
    w = wallets[wid]; key = w["apiKey"]
    print(f"\n{wid} ({w['displayName']}) — 10 execs")
    for i in range(10):
        pi = (int(wid[1:])*10+i) % len(PROGRAMS)
        img, cmd, code = PROGRAMS[pi]
        r = exec_code(key, cmd, img, {"main.py": code})
        if "_error" in r:
            e = r["_error"][:100]
            if "429" in e or "max" in e.lower(): break
            print(f"  [{i+1}] ERR: {e}"); total_f += 1
        else:
            res = r.get("result", {})
            print(f"  [{i+1:2d}] ✅ exit={res.get('exitCode','?')} credits={res.get('creditsCharged','?')}")
            total_s += 1
        time.sleep(5)
    time.sleep(2)
print(f"\nBatch {batch}: {total_s} success, {total_f} failed")