# stalwart-mcp

MCP server for [Stalwart](https://stalw.art/) mail server.

## Install

```
uvx --extra-index-url https://nikitatsym.github.io/stalwart-mcp/simple stalwart-mcp
```

## Configure

```json
{
  "mcpServers": {
    "stalwart": {
      "command": "uvx",
      "args": ["--refresh", "--extra-index-url", "https://nikitatsym.github.io/stalwart-mcp/simple", "stalwart-mcp"],
      "env": {
        "STALWART_URL": "https://mail.example.com",
        "STALWART_TOKEN": "your-api-key"
      }
    }
  }
}
```

## Groups

| Tool | Description |
|------|-------------|
| `stalwart_read` | Principals, settings, queue, reports, logs, telemetry, DNS (read-only) |
| `stalwart_write` | Create/update principals, settings, DKIM, spam training, queue management |
| `stalwart_delete` | Delete principals, queue messages, purge stores (destructive) |
| `stalwart_admin` | Reload, updates, diagnostics, store maintenance, reindex |

Call any group with `operation="help"` to list available operations.
