from .client import StalwartClient
from .registry import ROOT, Group, _op

# ── Client singleton ──────────────────────────────────────────────────

_client: StalwartClient | None = None


def _get_client() -> StalwartClient:
    global _client
    if _client is None:
        _client = StalwartClient()
    return _client


def _ok(data):
    if data is None:
        return {"status": "ok"}
    return data


# ── Slim helpers ──────────────────────────────────────────────────────

_SLIM_PRINCIPAL = {"id", "name", "type", "description", "emails"}


def _slim(item: dict, fields: set) -> dict:
    return {k: v for k, v in item.items() if k in fields}


def _slim_list(items: list, fields: set) -> list:
    return [_slim(i, fields) for i in items if isinstance(i, dict)]


# ── Groups ────────────────────────────────────────────────────────────

stalwart_read = Group(
    "stalwart_read",
    "Query Stalwart mail server data (safe, read-only).\n\n"
    "Call with operation=\"help\" to list all available read operations.\n"
    "Otherwise pass the operation name and a JSON object with parameters.\n\n"
    "Example: stalwart_read(operation=\"ListPrincipals\", "
    "params={\"types\": \"individual\", \"limit\": 20})",
)

stalwart_write = Group(
    "stalwart_write",
    "Create or update Stalwart resources (non-destructive).\n\n"
    "Call with operation=\"help\" to list all available write operations.\n"
    "Otherwise pass the operation name and a JSON object with parameters.\n\n"
    "Example: stalwart_write(operation=\"CreatePrincipal\", "
    "params={\"type\": \"individual\", \"name\": \"user@example.com\"})",
)

stalwart_delete = Group(
    "stalwart_delete",
    "Delete Stalwart resources (destructive, irreversible).\n\n"
    "Call with operation=\"help\" to list all available delete operations.\n"
    "Otherwise pass the operation name and a JSON object with parameters.\n\n"
    "Example: stalwart_delete(operation=\"DeletePrincipal\", "
    "params={\"id\": \"user@example.com\"})",
)

stalwart_admin = Group(
    "stalwart_admin",
    "Stalwart admin operations: reload, updates, diagnostics, maintenance.\n\n"
    "Call with operation=\"help\" to list all available admin operations.\n"
    "Otherwise pass the operation name and a JSON object with parameters.\n\n"
    "Example: stalwart_admin(operation=\"ReloadConfig\", params={\"dry_run\": true})",
)


# ── ROOT ──────────────────────────────────────────────────────────────

@_op(ROOT)
def stalwart_version():
    """Get the Stalwart MCP server version and service status."""
    from importlib.metadata import version

    try:
        _get_client().get_text("/healthz")
        service = {"status": "ok"}
    except Exception:
        service = {"status": "error"}
    return {"mcp": version("stalwart-mcp"), "service": service}


# ── stalwart_read ─────────────────────────────────────────────────────

@_op(stalwart_read)
def list_principals(
    types: str | None = None,
    page: int | None = None,
    limit: int = 20,
):
    """List principals. types: individual,group,list,domain,tenant,role,apiKey,oauthClient,resource,location."""
    params: dict = {"limit": limit}
    if types is not None:
        params["types"] = types
    if page is not None:
        params["page"] = page
    result = _get_client().get("/api/principal", params=params)
    if isinstance(result, dict) and "data" in result:
        data = result["data"]
        if isinstance(data, dict) and "items" in data:
            data["items"] = _slim_list(data["items"], _SLIM_PRINCIPAL)
        return result
    if isinstance(result, list):
        return _slim_list(result, _SLIM_PRINCIPAL)
    return _ok(result)


@_op(stalwart_read)
def show_principal(id: str):
    """Get full principal details by ID."""
    return _ok(_get_client().get(f"/api/principal/{id}"))


@_op(stalwart_read)
def get_queue_status():
    """Get mail queue processing status."""
    return _ok(_get_client().get("/api/queue/status"))


@_op(stalwart_read)
def list_queue_messages(
    page: int | None = None,
    limit: int = 20,
    values: str | None = None,
):
    """List queued messages. values: filter string."""
    params: dict = {"limit": limit}
    if page is not None:
        params["page"] = page
    if values is not None:
        params["values"] = values
    return _ok(_get_client().get("/api/queue/messages", params=params))


@_op(stalwart_read)
def show_queue_message(id: int):
    """Get full details of a queued message."""
    return _ok(_get_client().get(f"/api/queue/messages/{id}"))


@_op(stalwart_read)
def list_queued_reports(
    page: int | None = None,
    limit: int = 20,
):
    """List queued delivery reports."""
    params: dict = {"limit": limit}
    if page is not None:
        params["page"] = page
    return _ok(_get_client().get("/api/queue/reports", params=params))


@_op(stalwart_read)
def list_dmarc_reports(
    page: int | None = None,
    limit: int = 20,
):
    """List incoming DMARC reports."""
    params: dict = {"limit": limit}
    if page is not None:
        params["page"] = page
    return _ok(_get_client().get("/api/reports/dmarc", params=params))


@_op(stalwart_read)
def list_tls_reports(
    page: int | None = None,
    limit: int = 20,
):
    """List incoming TLS reports."""
    params: dict = {"limit": limit}
    if page is not None:
        params["page"] = page
    return _ok(_get_client().get("/api/reports/tls", params=params))


@_op(stalwart_read)
def list_arf_reports(
    page: int | None = None,
    limit: int = 20,
):
    """List incoming ARF/abuse reports."""
    params: dict = {"limit": limit}
    if page is not None:
        params["page"] = page
    return _ok(_get_client().get("/api/reports/arf", params=params))


@_op(stalwart_read)
def get_settings_by_keys(
    keys: list | None = None,
    prefixes: list | None = None,
):
    """Get settings by specific keys or prefixes."""
    params: dict = {}
    if keys is not None:
        params["keys"] = keys
    if prefixes is not None:
        params["prefixes"] = prefixes
    return _ok(_get_client().get("/api/settings/keys", params=params))


@_op(stalwart_read)
def get_settings_by_group(
    prefix: str | None = None,
    suffix: str | None = None,
    page: int | None = None,
    limit: int = 20,
):
    """Get settings by group prefix/suffix."""
    params: dict = {"limit": limit}
    if prefix is not None:
        params["prefix"] = prefix
    if suffix is not None:
        params["suffix"] = suffix
    if page is not None:
        params["page"] = page
    return _ok(_get_client().get("/api/settings/group", params=params))


@_op(stalwart_read)
def list_settings(prefix: str | None = None):
    """List all settings, optionally filtered by prefix."""
    params: dict = {}
    if prefix is not None:
        params["prefix"] = prefix
    return _ok(_get_client().get("/api/settings/list", params=params))


@_op(stalwart_read)
def list_logs(
    page: int | None = None,
    limit: int = 20,
):
    """List server logs."""
    params: dict = {"limit": limit}
    if page is not None:
        params["page"] = page
    return _ok(_get_client().get("/api/logs", params=params))


@_op(stalwart_read)
def list_metrics(after: str | None = None):
    """List telemetry metrics. after: timestamp filter."""
    params: dict = {}
    if after is not None:
        params["after"] = after
    return _ok(_get_client().get("/api/telemetry/metrics", params=params))


@_op(stalwart_read)
def list_traces(
    type: str | None = None,
    page: int | None = None,
    limit: int = 20,
):
    """List telemetry traces."""
    params: dict = {"limit": limit}
    if type is not None:
        params["type"] = type
    if page is not None:
        params["page"] = page
    return _ok(_get_client().get("/api/telemetry/traces", params=params))


@_op(stalwart_read)
def show_trace(id: str):
    """Get full trace details by ID."""
    return _ok(_get_client().get(f"/api/telemetry/trace/{id}"))


@_op(stalwart_read)
def get_dns_records(domain: str):
    """Get DNS records for a domain."""
    return _ok(_get_client().get(f"/api/dns/records/{domain}"))


@_op(stalwart_read)
def list_deleted_messages(
    account_id: str,
    page: int | None = None,
    limit: int = 20,
):
    """List deleted messages for an account (available for restore)."""
    params: dict = {"limit": limit}
    if page is not None:
        params["page"] = page
    return _ok(_get_client().get(f"/api/store/undelete/{account_id}", params=params))


@_op(stalwart_read)
def get_blob(blob_id: str, limit: int | None = None):
    """Get raw blob content by ID."""
    params: dict = {}
    if limit is not None:
        params["limit"] = limit
    return _ok(_get_client().get_text(f"/api/store/blobs/{blob_id}", params=params))


# ── stalwart_write ────────────────────────────────────────────────────

@_op(stalwart_write)
def create_principal(
    type: str,
    name: str,
    description: str | None = None,
    quota: int | None = None,
    secrets: list | None = None,
    emails: list | None = None,
    urls: list | None = None,
    memberOf: list | None = None,
    roles: list | None = None,
    lists: list | None = None,
    members: list | None = None,
    enabledPermissions: list | None = None,
    disabledPermissions: list | None = None,
    externalMembers: list | None = None,
):
    """Create a principal. type: individual,group,list,domain,tenant,role,apiKey,oauthClient,resource,location."""
    body: dict = {"type": type, "name": name}
    if description is not None:
        body["description"] = description
    if quota is not None:
        body["quota"] = quota
    if secrets is not None:
        body["secrets"] = secrets
    if emails is not None:
        body["emails"] = emails
    if urls is not None:
        body["urls"] = urls
    if memberOf is not None:
        body["memberOf"] = memberOf
    if roles is not None:
        body["roles"] = roles
    if lists is not None:
        body["lists"] = lists
    if members is not None:
        body["members"] = members
    if enabledPermissions is not None:
        body["enabledPermissions"] = enabledPermissions
    if disabledPermissions is not None:
        body["disabledPermissions"] = disabledPermissions
    if externalMembers is not None:
        body["externalMembers"] = externalMembers
    return _ok(_get_client().post("/api/principal", json=body))


@_op(stalwart_write)
def update_principal(id: str, changes: list):
    """Update a principal. changes: array of {action, field, value} objects. action: set,addItem,removeItem."""
    return _ok(_get_client().patch(f"/api/principal/{id}", json=changes))


@_op(stalwart_write)
def start_queue():
    """Resume mail queue processing."""
    return _ok(_get_client().patch("/api/queue/status/start"))


@_op(stalwart_write)
def stop_queue():
    """Pause mail queue processing."""
    return _ok(_get_client().patch("/api/queue/status/stop"))


@_op(stalwart_write)
def reschedule_messages(filter: str | None = None):
    """Bulk reschedule queued messages. filter: query string."""
    params: dict = {}
    if filter is not None:
        params["filter"] = filter
    return _ok(_get_client().patch("/api/queue/messages", params=params))


@_op(stalwart_write)
def reschedule_message(id: int):
    """Reschedule a single queued message."""
    return _ok(_get_client().patch(f"/api/queue/messages/{id}"))


@_op(stalwart_write)
def update_settings(settings: list):
    """Update settings. settings: array of {type, prefix, ...} objects."""
    return _ok(_get_client().post("/api/settings", json=settings))


@_op(stalwart_write)
def generate_dkim(
    id: str,
    algorithm: str | None = None,
    domain: str | None = None,
    selector: str | None = None,
):
    """Generate DKIM keys. Returns DKIM DNS record."""
    body: dict = {"id": id}
    if algorithm is not None:
        body["algorithm"] = algorithm
    if domain is not None:
        body["domain"] = domain
    if selector is not None:
        body["selector"] = selector
    return _ok(_get_client().post("/api/dkim", json=body))


@_op(stalwart_write)
def train_spam(message: str):
    """Train global spam classifier with a spam message."""
    return _ok(_get_client().post("/api/spam-filter/train/spam", content=message, headers={"Content-Type": "text/plain"}))


@_op(stalwart_write)
def train_ham(message: str):
    """Train global spam classifier with a ham (not spam) message."""
    return _ok(_get_client().post("/api/spam-filter/train/ham", content=message, headers={"Content-Type": "text/plain"}))


@_op(stalwart_write)
def train_account_spam(account_id: str, message: str):
    """Train per-account spam classifier with a spam message."""
    return _ok(_get_client().post(f"/api/spam-filter/train/spam/{account_id}", content=message, headers={"Content-Type": "text/plain"}))


@_op(stalwart_write)
def train_account_ham(account_id: str, message: str):
    """Train per-account spam classifier with a ham (not spam) message."""
    return _ok(_get_client().post(f"/api/spam-filter/train/ham/{account_id}", content=message, headers={"Content-Type": "text/plain"}))


@_op(stalwart_write)
def classify_spam(
    message: str,
    remote_ip: str | None = None,
    ehlo_domain: str | None = None,
    authenticated_as: str | None = None,
    is_tls: bool | None = None,
    env_from: str | None = None,
    env_from_flags: str | None = None,
    env_rcpt_to: list | None = None,
):
    """Test spam classification for a message."""
    body: dict = {"message": message}
    if remote_ip is not None:
        body["remoteIp"] = remote_ip
    if ehlo_domain is not None:
        body["ehloDomain"] = ehlo_domain
    if authenticated_as is not None:
        body["authenticatedAs"] = authenticated_as
    if is_tls is not None:
        body["isTls"] = is_tls
    if env_from is not None:
        body["envFrom"] = env_from
    if env_from_flags is not None:
        body["envFromFlags"] = env_from_flags
    if env_rcpt_to is not None:
        body["envRcptTo"] = env_rcpt_to
    return _ok(_get_client().post("/api/spam-filter/classify", json=body))


@_op(stalwart_write)
def restore_deleted_messages(account_id: str, messages: list):
    """Restore deleted messages. messages: array of {hash, collection, restoreTime, cancelDeletion}."""
    return _ok(_get_client().post(f"/api/store/undelete/{account_id}", json=messages))


@_op(stalwart_write)
def update_encryption(
    type: str | None = None,
    algo: str | None = None,
    certs: str | None = None,
):
    """Update encryption-at-rest settings."""
    body: dict = {}
    if type is not None:
        body["type"] = type
    if algo is not None:
        body["algo"] = algo
    if certs is not None:
        body["certs"] = certs
    return _ok(_get_client().post("/api/account/crypto", json=body))


@_op(stalwart_write)
def update_auth(
    type: str | None = None,
    totp_token: str | None = None,
    app_passwords: list | None = None,
):
    """Update authentication settings (2FA, app passwords)."""
    body: dict = {}
    if type is not None:
        body["type"] = type
    if totp_token is not None:
        body["totpToken"] = totp_token
    if app_passwords is not None:
        body["appPasswords"] = app_passwords
    return _ok(_get_client().post("/api/account/auth", json=body))


# ── stalwart_delete ───────────────────────────────────────────────────

@_op(stalwart_delete)
def delete_principal(id: str):
    """Delete a principal. Irreversible."""
    return _ok(_get_client().delete(f"/api/principal/{id}"))


@_op(stalwart_delete)
def delete_queue_messages(text: str | None = None):
    """Bulk delete queued messages by filter text."""
    params: dict = {}
    if text is not None:
        params["text"] = text
    return _ok(_get_client().delete("/api/queue/messages", params=params))


@_op(stalwart_delete)
def delete_queue_message(id: int):
    """Delete a single queued message."""
    return _ok(_get_client().delete(f"/api/queue/messages/{id}"))


@_op(stalwart_delete)
def purge_blobs():
    """Purge unreferenced blobs from store."""
    return _ok(_get_client().get("/api/store/purge/blob"))


@_op(stalwart_delete)
def purge_data():
    """Purge data store."""
    return _ok(_get_client().get("/api/store/purge/data"))


@_op(stalwart_delete)
def purge_cache():
    """Purge in-memory cache."""
    return _ok(_get_client().get("/api/store/purge/in-memory"))


@_op(stalwart_delete)
def purge_all_accounts():
    """Purge all account data."""
    return _ok(_get_client().get("/api/store/purge/account"))


@_op(stalwart_delete)
def purge_account(account_id: str):
    """Purge a single account's data."""
    return _ok(_get_client().get(f"/api/store/purge/account/{account_id}"))


@_op(stalwart_delete)
def delete_global_bayes():
    """Delete global Bayes spam model."""
    return _ok(_get_client().get("/api/store/purge/in-memory/default/bayes-global"))


@_op(stalwart_delete)
def delete_account_bayes(account_id: str):
    """Delete per-account Bayes spam model."""
    return _ok(_get_client().get(f"/api/store/purge/in-memory/default/bayes-account/{account_id}"))


@_op(stalwart_delete)
def reset_imap_uids(account_id: str):
    """Reset IMAP UIDs for an account."""
    return _ok(_get_client().delete(f"/api/store/uids/{account_id}"))


# ── stalwart_admin ────────────────────────────────────────────────────

@_op(stalwart_admin)
def reload_config(dry_run: bool = False):
    """Reload server configuration. Returns warnings and errors."""
    params: dict = {}
    if dry_run:
        params["dry-run"] = "true"
    return _ok(_get_client().get("/api/reload", params=params))


@_op(stalwart_admin)
def update_spam_filter():
    """Update spam filter databases."""
    return _ok(_get_client().get("/api/update/spam-filter"))


@_op(stalwart_admin)
def update_webadmin():
    """Update web admin UI."""
    return _ok(_get_client().get("/api/update/webadmin"))


@_op(stalwart_admin)
def reindex():
    """Rebuild full-text search index."""
    return _ok(_get_client().get("/api/store/reindex"))


@_op(stalwart_admin)
def get_diagnostics_token():
    """Get diagnostics/troubleshooting token."""
    return _ok(_get_client().get("/api/troubleshoot/token"))


@_op(stalwart_admin)
def validate_dmarc(
    remote_ip: str,
    ehlo_domain: str,
    mail_from: str,
    body: str,
):
    """Validate DMARC for a message. Returns SPF, DKIM, ARC, DMARC results."""
    payload: dict = {
        "remoteIp": remote_ip,
        "ehloDomain": ehlo_domain,
        "mailFrom": mail_from,
        "body": body,
    }
    return _ok(_get_client().post("/api/troubleshoot/dmarc", json=payload))


@_op(stalwart_admin)
def get_metrics_token():
    """Get token for live metrics streaming."""
    return _ok(_get_client().get("/api/telemetry/live/metrics-token"))


@_op(stalwart_admin)
def get_tracing_token():
    """Get token for live trace streaming."""
    return _ok(_get_client().get("/api/telemetry/live/tracing-token"))


@_op(stalwart_admin)
def get_encryption_settings():
    """Get encryption-at-rest settings."""
    return _ok(_get_client().get("/api/account/crypto"))


@_op(stalwart_admin)
def get_auth_settings():
    """Get authentication settings (2FA, app passwords)."""
    return _ok(_get_client().get("/api/account/auth"))
