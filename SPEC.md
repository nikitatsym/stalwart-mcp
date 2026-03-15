---
tags: [mcp, python, task]
domain: dev
type: task
---

# stalwart-mcp

MCP server for [Stalwart](https://stalw.art/) mail server.

- **MCP standard:** `/home/ari/src/obsidian_vault/specs/mcp-server.md` — follow it exactly (structure, registry, server dispatch, groups, config, client patterns)
- **API base:** `{STALWART_URL}/api`, auth: `Authorization: Bearer <token>` (API key) or Basic auth
- **OpenAPI spec:** https://github.com/stalwartlabs/mail-server/blob/main/api/v1/openapi.yml
- **Docs:** https://stalw.art/docs/api/management/overview/
- **Health:** `GET /healthz` (200 = running)
- **Hosting:** GitHub — CI/CD from `/home/ari/src/vastai-mcp/.github/workflows/build.yml`, enable Pages (Actions source), create `docs/index.html` setup page

## Config

```
STALWART_URL      — base URL (e.g. https://mail.example.com)
STALWART_TOKEN    — API key (Bearer)
```

## Groups

stalwart_read     — principals, settings, queue status, reports, logs, telemetry, DNS records (safe, read-only)
stalwart_write    — create/update principals, settings, DKIM, spam training, queue management (non-destructive)
stalwart_delete   — delete principals, queue messages, purge stores (destructive, irreversible)
stalwart_admin    — reload, updates, diagnostics, store maintenance, reindex

## Operations

### stalwart_read

| Operation | Endpoint | Notes |
|---|---|---|
| **Principals** | | |
| `list_principals(types, page, limit)` | `GET /principal` | Query: `types` = individual,group,list,domain,tenant,role,apiKey,oauthClient,resource,location. Slim |
| `show_principal(id)` | `GET /principal/{id}` | Full |
| **Queue** | | |
| `get_queue_status()` | `GET /queue/status` | Returns boolean |
| `list_queue_messages(page, limit)` | `GET /queue/messages` | Query: `values` for filter |
| `show_queue_message(id)` | `GET /queue/messages/{id}` | Full |
| **Reports** | | |
| `list_queued_reports(page, limit)` | `GET /queue/reports` | Delivery reports |
| `list_dmarc_reports(page, limit)` | `GET /reports/dmarc` | Incoming DMARC |
| `list_tls_reports(page, limit)` | `GET /reports/tls` | Incoming TLS |
| `list_arf_reports(page, limit)` | `GET /reports/arf` | Incoming ARF/abuse |
| **Settings** | | |
| `get_settings_by_keys(keys, prefixes)` | `GET /settings/keys` | |
| `get_settings_by_group(prefix, suffix, page, limit)` | `GET /settings/group` | |
| `list_settings(prefix)` | `GET /settings/list` | |
| **Logs** | | |
| `list_logs(page, limit)` | `GET /logs` | |
| **Telemetry** | | |
| `list_metrics(after)` | `GET /telemetry/metrics` | |
| `list_traces(type, page, limit)` | `GET /telemetry/traces` | |
| `show_trace(id)` | `GET /telemetry/trace/{id}` | |
| **DNS** | | |
| `get_dns_records(domain)` | `GET /dns/records/{domain}` | |
| **Store** | | |
| `list_deleted_messages(account_id, page, limit)` | `GET /store/undelete/{account_id}` | |
| `get_blob(blob_id, limit)` | `GET /store/blobs/{blob_id}` | Raw content |

Total: 19

### stalwart_write

| Operation | Endpoint | Notes |
|---|---|---|
| **Principals** | | |
| `create_principal(type, name, ...)` | `POST /principal` | Required: type, name. Optional: description, quota, secrets, emails, urls, memberOf, roles, lists, members, enabledPermissions, disabledPermissions, externalMembers |
| `update_principal(id, ...)` | `PATCH /principal/{id}` | Body: array of `{action, field, value}` |
| **Queue** | | |
| `start_queue()` | `PATCH /queue/status/start` | Resume processing |
| `stop_queue()` | `PATCH /queue/status/stop` | Pause processing |
| `reschedule_messages(filter)` | `PATCH /queue/messages` | Bulk reschedule |
| `reschedule_message(id)` | `PATCH /queue/messages/{id}` | Single |
| **Settings** | | |
| `update_settings(...)` | `POST /settings` | Body: array of `{type, prefix, ...}` |
| **DKIM** | | |
| `generate_dkim(id, algorithm, domain, selector)` | `POST /dkim` | Returns DKIM DNS record |
| **Spam Filter** | | |
| `train_spam(message)` | `POST /spam-filter/train/spam` | Global classifier |
| `train_ham(message)` | `POST /spam-filter/train/ham` | Global classifier |
| `train_account_spam(account_id, message)` | `POST /spam-filter/train/spam/{account_id}` | Per-account |
| `train_account_ham(account_id, message)` | `POST /spam-filter/train/ham/{account_id}` | Per-account |
| `classify_spam(message, remote_ip, ...)` | `POST /spam-filter/classify` | Test classification. Body: message, remoteIp, ehloDomain, authenticatedAs, isTls, envFrom, envFromFlags, envRcptTo |
| **Store** | | |
| `restore_deleted_messages(account_id, messages)` | `POST /store/undelete/{account_id}` | Body: `[{hash, collection, restoreTime, cancelDeletion}]` |
| **Account** | | |
| `update_encryption(type, algo, certs)` | `POST /account/crypto` | Encryption-at-rest |
| `update_auth(...)` | `POST /account/auth` | 2FA, app passwords |

Total: 16

### stalwart_delete

| Operation | Endpoint | Notes |
|---|---|---|
| **Principals** | | |
| `delete_principal(id)` | `DELETE /principal/{id}` | |
| **Queue** | | |
| `delete_queue_messages(text)` | `DELETE /queue/messages` | Bulk by filter |
| `delete_queue_message(id)` | `DELETE /queue/messages/{id}` | Single |
| **Store** | | |
| `purge_blobs()` | `GET /store/purge/blob` | Unreferenced blobs |
| `purge_data()` | `GET /store/purge/data` | Data store |
| `purge_cache()` | `GET /store/purge/in-memory` | In-memory cache |
| `purge_all_accounts()` | `GET /store/purge/account` | All account data |
| `purge_account(account_id)` | `GET /store/purge/account/{account_id}` | Single account |
| `delete_global_bayes()` | `GET /store/purge/in-memory/default/bayes-global` | Global Bayes model |
| `delete_account_bayes(account_id)` | `GET /store/purge/in-memory/default/bayes-account/{account_id}` | Per-account Bayes |
| `reset_imap_uids(account_id)` | `DELETE /store/uids/{account_id}` | Reset IMAP UIDs |

Total: 11

### stalwart_admin

| Operation | Endpoint | Notes |
|---|---|---|
| **Reload** | | |
| `reload_config(dry_run)` | `GET /reload` | Query: `dry-run`. Returns `{warnings, errors}` |
| **Updates** | | |
| `update_spam_filter()` | `GET /update/spam-filter` | Update spam filter DBs |
| `update_webadmin()` | `GET /update/webadmin` | Update web admin UI |
| **Store** | | |
| `reindex()` | `GET /store/reindex` | Full-text search reindex |
| **Diagnostics** | | |
| `get_diagnostics_token()` | `GET /troubleshoot/token` | |
| `validate_dmarc(remote_ip, ehlo_domain, mail_from, body)` | `POST /troubleshoot/dmarc` | Returns SPF, DKIM, ARC, DMARC results |
| **Telemetry tokens** | | |
| `get_metrics_token()` | `GET /telemetry/live/metrics-token` | For live metrics streaming |
| `get_tracing_token()` | `GET /telemetry/live/tracing-token` | For live trace streaming |
| **Account (self-service)** | | |
| `get_encryption_settings()` | `GET /account/crypto` | |
| `get_auth_settings()` | `GET /account/auth` | 2FA, app passwords |

Total: 10

## Slim fields

```
SLIM_PRINCIPAL = {"id", "name", "type", "description", "emails"}
```

## Deploy checklist

- [ ] CI/CD workflow (`.github/workflows/build.yml`)
- [ ] GitHub: enable Pages in repo settings (source: GitHub Actions) — `gh api repos/OWNER/REPO/pages -X POST -f build_type=workflow`
- [ ] GitHub: `docs/index.html` setup page (API key input → config JSON generator)
- [ ] First push to `main` triggers build → tag v1.0.0 → release with wheel → PEP 503 index
- [ ] Verify install: `uvx --extra-index-url INDEX_URL stalwart-mcp`
