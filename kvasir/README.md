# Kvasir

Exposes Home Assistant's pending updates (Core, Supervisor, OS, add-ons,
HACS integrations — anything with an `update.*` entity) as MCP tools, so an
MCP client such as Claude Code can list, install, or skip them.

Named for the god born from the pooled wisdom of the Æsir and Vanir —
knows the state of everything, including what's due for an update.

## Tools

- `list_pending_updates` — entities in the `update` domain with `state: on`
  (an update is available), including installed/latest version and release
  notes URL.
- `install_update(entity_id, backup=True)` — calls `update.install`.
  `backup` is honored on entities that support it (e.g. Supervisor,
  add-ons); ignored elsewhere.
- `skip_update(entity_id)` — calls `update.skip`.

## Configuration

| Option | Description |
|---|---|
| `api_key` | Required. Bearer token clients must send to reach this server. Generate a random string, e.g. `openssl rand -hex 32`. |
| `log_level` | `debug` \| `info` \| `warning` \| `error` |

## Connecting from Claude Code

```
claude mcp add kvasir \
  --transport sse http://homeassistant:8321/sse \
  --header "Authorization: Bearer <api_key>"
```

No `HA_TOKEN` is needed — the add-on talks to Home Assistant's REST API
through the Supervisor proxy using an auto-injected, scoped token.
