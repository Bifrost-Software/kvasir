"""Kvasir: MCP server exposing Home Assistant's `update.*` entities as tools.

Runs inside the Kvasir add-on. Talks to Home Assistant's REST API through
the Supervisor proxy (http://supervisor/core), authenticated with the
SUPERVISOR_TOKEN that HA injects automatically because the add-on declares
`homeassistant_api: true` in config.yaml. Callers (e.g. Claude Code)
authenticate to *this* server with a separate bearer token set via the
add-on's `api_key` option.
"""

import logging
import os

import requests
import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse

# UpdateEntityFeature.BACKUP, see homeassistant.components.update.const
UPDATE_FEATURE_BACKUP = 4

HA_URL = os.environ.get("HA_URL", "http://supervisor/core")
HA_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
API_KEY = os.environ["API_KEY"]
PORT = int(os.environ.get("PORT", "8321"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info").upper()

logging.basicConfig(level=LOG_LEVEL)
log = logging.getLogger("kvasir")

mcp = FastMCP("kvasir")


def _ha_headers() -> dict:
    return {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}


@mcp.tool()
def list_pending_updates() -> list[dict]:
    """List Home Assistant update.* entities that currently have an update available."""
    resp = requests.get(f"{HA_URL}/api/states", headers=_ha_headers(), timeout=10)
    resp.raise_for_status()
    updates = []
    for entity in resp.json():
        if not entity["entity_id"].startswith("update.") or entity["state"] != "on":
            continue
        attrs = entity.get("attributes", {})
        updates.append(
            {
                "entity_id": entity["entity_id"],
                "name": attrs.get("friendly_name", entity["entity_id"]),
                "installed_version": attrs.get("installed_version"),
                "latest_version": attrs.get("latest_version"),
                "release_url": attrs.get("release_url"),
                "supports_backup": bool(attrs.get("supported_features", 0) & UPDATE_FEATURE_BACKUP),
            }
        )
    return updates


@mcp.tool()
def install_update(entity_id: str, backup: bool = True) -> str:
    """Install a pending update for the given update.* entity_id.

    Set backup=True (default) to request a backup first on entities that
    support it (e.g. Supervisor, add-ons). Ignored where unsupported.
    """
    if not entity_id.startswith("update."):
        raise ValueError("entity_id must be an update.* entity, e.g. update.home_assistant_core_update")
    payload = {"entity_id": entity_id, "backup": backup}
    resp = requests.post(
        f"{HA_URL}/api/services/update/install", headers=_ha_headers(), json=payload, timeout=30
    )
    resp.raise_for_status()
    return f"Install triggered for {entity_id}"


@mcp.tool()
def skip_update(entity_id: str) -> str:
    """Mark a pending update as skipped so it stops showing as available until the next release."""
    if not entity_id.startswith("update."):
        raise ValueError("entity_id must be an update.* entity")
    resp = requests.post(
        f"{HA_URL}/api/services/update/skip", headers=_ha_headers(), json={"entity_id": entity_id}, timeout=10
    )
    resp.raise_for_status()
    return f"Skipped {entity_id}"


class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.headers.get("authorization") != f"Bearer {API_KEY}":
            return PlainTextResponse("Unauthorized", status_code=401)
        return await call_next(request)


app = mcp.sse_app()
app.add_middleware(BearerAuthMiddleware)

if __name__ == "__main__":
    log.info("Listening on 0.0.0.0:%s", PORT)
    uvicorn.run(app, host="0.0.0.0", port=PORT)
