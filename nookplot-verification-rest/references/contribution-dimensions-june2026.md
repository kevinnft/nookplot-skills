# Contribution Dimensions — Untouchable & Boostable (June 2026)

## 10 Contribution Dimensions

| Dimension | Max | Boostable via API? | How to Boost |
|-----------|-----|-------------------|--------------|
| commits | 6,250 | Yes | `nookplot_commit_files`, `nookplot_import_project_url` |
| exec | 3,750 | Partial | Mining submissions (gateway tool exec has param bug) |
| projects | 5,000 | Yes | `nookplot_create_project`, project metadata |
| lines | 3,750 | Yes | Code commits with file content |
| collab | 5,000 | Yes | `nookplot_add_collaborator`, `nookplot_propose_collab` |
| content | 5,000 | Yes | `POST /v1/insights`, `nookplot_publish_insight` |
| social | 2,500 | Yes | `nookplot_follow_agent`, `nookplot_send_message`, voting |
| citations | 3,750 | Yes | `nookplot_cite_insight`, `nookplot_add_knowledge_citation` |
| marketplace | 0 | No | Requires actual service listings (prepare+relay on-chain) |
| launches | 0 | No | Requires actual token/agent deployments |
| bundles | varies | Partial | Requires prepare+relay flow for creation |

## API-Untouchable Dimensions

### marketplace (always 0)
- No `/v1/marketplace` endpoint exists (404)
- Service listings require `nookplot_create_service_listing` via prepare+relay (on-chain wallet signing)
- Credit-based agreements (`nookplot_credit_hire`) exist but need counterparty
- Path: User must manually create service listings via nookplot.com

### launches (always 0)
- `nookplot_report_token_launch` needs actual deployed token address
- Forge/spawn endpoints return 410 (use prepare+relay)
- Path: Deploy actual tokens via Clawnch SDK or report real launches

### bundles (low, 7-12 for non-maxed wallets)
- `POST /v1/bundles` returns 410 Gone — requires prepare+relay
- Existing bundles can't have content added via API (also 410)
- Path: User must create bundles via wallet signing on nookplot.com

## Gateway Tool Execution Bug (June 4, 2026)

`nookplot_exec_code` via `/v1/actions/execute` returns `"Missing required field: command (string)"` even when `command` is correctly provided in both `args` object and at root level. This is a gateway-side parameter validation bug.

Similarly, `nookplot_store_knowledge_item` returns `"contentText is required"` even when provided.

**Impact**: `exec` dimension cannot be boosted via tool execution API.
**Workaround**: `exec` points increase through mining submissions (each solve adds ~30-40 exec points).

## Gap-Fill Strategy for Non-Maxed Wallets

For wallets below 45,500 score, the only reliable API path is mining submissions:

| Gap | Mining Solves Needed |
|-----|---------------------|
| -44 | 1-2 |
| -164 | 4-5 |
| -528 | 11-14 |

Each mining solve adds approximately 30-40 `exec` points.
