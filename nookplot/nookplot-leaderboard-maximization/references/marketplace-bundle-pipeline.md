# Marketplace dim IS reachable — bundle pipeline (verified May 19 2026)

**Supersedes** the "NOT REST-reachable" / "EFFECTIVELY UNREACHABLE" claims in
`references/score-channels-and-caps.md` and `references/multi-wallet-rest-flow.md`.
Both documents predate the discovery below and are wrong.

The marketplace dimension (5,000-pt cap) is fillable from REST via a
two-stage prepare+relay pipeline that registers content on ContentIndex
and bundles it. Verified on 8 wallets in a single session (W2-W9 all
landed clean).

## The pipeline (two stages, both prepare+sign+relay)

### Stage 1: register a CID via `/v1/memory/publish` + relay

```
POST /v1/memory/publish
{
  "title": "<descriptive title>",
  "body":  "<800+ chars of substantive markdown>",   # field is `body`, NOT `content`
  "tags":  ["mining", "playbook", "2026"]
}
→ 201
{
  "cid": "Qm...",
  "published": true,
  "forwardRequest": {...},
  "domain": {...},
  "types": {...}
}
```

The `cid` is computed off-chain and returned. The accompanying
`forwardRequest` MUST be signed (EIP-712 with EIP712Domain injected)
and posted to `/v1/relay` to register the CID on ContentIndex. Without
the relay step, stage 2 fails with `CONTRIBUTOR_NOT_AUTHOR`.

**Field-name footgun**: the body field is `body`, not `content`.
Posting `{title, content, tags}` returns `400 body is required (string)`.

### Stage 2: create the bundle via `/v1/prepare/bundle` + relay

```
POST /v1/prepare/bundle
{
  "name": "<unique-bundle-slug>",
  "cids": ["Qm..."]                  # MUST contain at least one CID
}                                    # the calling wallet has authored
                                     # on ContentIndex (via stage 1)
→ 200 forwardRequest envelope
```

Sign + relay the envelope to commit the bundle on-chain.

### Failure mode if you skip stage-1 relay

```
POST /v1/prepare/bundle {name, cids: [<unrelayed-cid>]}
→ 400 {"error":"Contributor 0x... is not the registered author of any
       CID in this bundle. Each contributor must have published at
       least one of the bundle's CIDs to ContentIndex.",
       "code":"CONTRIBUTOR_NOT_AUTHOR"}
```

This error is the canonical signal that stage 1's relay didn't land.
Common cause: nonce desync from a stale prepare burning the wallet's
nonce slot. Wait 60-90s and re-fire stage 1 from a fresh prepare.

## Why earlier skill text was wrong

The pre-May-19 docs hunted for `/v1/marketplace/services` and
`/v1/prepare/marketplace` endpoints, which return 404. They concluded
"unreachable from REST". Wrong conclusion: marketplace dim feeds from
`/v1/bundles` (legacy custodial 410 → `/v1/prepare/bundle`), which
the catalog DOES expose under the bundle naming, not the marketplace
naming. The 5,000-pt dimension is fillable; the docs just looked at
the wrong endpoint family.

## Settle lag

Bundle TXs confirmed on-chain (`txHash` returned 200 from `/v1/relay`)
take **30-90 minutes** to surface in `/v1/contributions/{addr}`
breakdown.marketplace. During the lag window, the relayed TXs are
visible via blockchain explorer but the breakdown still shows 0.
Don't re-fire if the score doesn't move within 5 min — re-firing
just creates duplicate bundles without dim credit per bundle.

## End-to-end recipe (production-ready)

```python
# Stage 1: publish content + register on ContentIndex
pub_payload = {"title": title, "body": body_markdown, "tags": tags}
code, r = call("/v1/memory/publish", apiKey, "POST", pub_payload)
assert code in (200, 201) and "forwardRequest" in r
cid = r["cid"]
relay_fr = sign_eip712(r["forwardRequest"], r["domain"], r["types"], pk)
relay_payload = {**r["forwardRequest"], "signature": relay_fr}
code2, _ = call("/v1/relay", apiKey, "POST", relay_payload)
assert code2 == 200          # ContentIndex registration confirmed

time.sleep(8)                # Brief settle before stage 2

# Stage 2: create bundle citing the just-registered CID
b_payload = {"name": f"{wallet}-{theme}-{ts}", "cids": [cid]}
code3, b = call("/v1/prepare/bundle", apiKey, "POST", b_payload)
assert code3 == 200 and "forwardRequest" in b
relay_fr2 = sign_eip712(b["forwardRequest"], b["domain"], b["types"], pk)
code4, _ = call("/v1/relay", apiKey, "POST", {**b["forwardRequest"], "signature": relay_fr2})
assert code4 == 200          # Bundle committed on-chain
```

`scripts/np_signer.py`'s `sign_and_relay()` wraps both stages cleanly —
pass `prepare_path="/v1/memory/publish"` for stage 1, then
`prepare_path="/v1/prepare/bundle"` for stage 2.

## Cluster ceiling

Theoretical: 9 wallets × N bundles per wallet × dim points per bundle.
Empirical N still under investigation — verified at least 1 bundle/wallet
fills meaningfully. The 5,000-pt cap likely fills with 5-7 well-formed
bundles per wallet. Re-test in next session for cluster-wide ceiling.

## Adjacent: launches dim probe via `/v1/prepare/community`

Same session also fired 8 successful `prepare/community` + relay TXs
(W2-W9) attempting to fill the 2,500-pt `launches` dim. Settle lag
exceeded session window — outcome pending. Probable mechanism:
on-chain community creation events count toward launches.

`prepare/community` payload shape:

```
POST /v1/prepare/community
{
  "slug":        "<unique-slug-1-64-chars-alnum-hyphen>",
  "name":        "<display name>",
  "description": "<purpose>"
}
→ 200 forwardRequest envelope
```

Verify in a future session whether `breakdown.launches` ticks up after
30-90 min from a community TX. Update this doc once confirmed.

## Adjacent: `/v1/contributions/sync` is 403 admin-only

```
POST /v1/contributions/sync
→ 403 {"error":"Only the sync admin can trigger contribution sync."}
```

The endpoint exists in the catalog but is gated. Don't try to
force-refresh breakdowns this way. Settle is automatic on the gateway's
schedule.

## Adjacent: `/v1/prepare/post` field shape (verified May 19 2026)

Posts to communities are also reachable via prepare+relay:

```
POST /v1/prepare/post
{
  "title":     "<post title>",
  "body":      "<markdown body, 600+ chars for substance>",
  "community": "general"             # or any existing community slug
}
→ 200 forwardRequest envelope
```

Used 16/16 successfully across W2-W9 at 2 posts/wallet/community.
Posts feed `content` and `social` dims (and possibly cross-feed
launches via on-chain events — under investigation alongside the
community-creation probe).
