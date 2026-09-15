# Development

## Iterating on `server.py` without rebuilding the add-on

The MCP server itself has no Home-Assistant-specific dependency other than
an HTTP endpoint + bearer token, so you can run it directly on your dev
machine against your real HA instance while you iterate:

```bash
cd kvasir/app
python3 -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

export HA_URL="http://homeassistant:8123"      # note: no add-on proxy here
export SUPERVISOR_TOKEN="<a long-lived access token>"  # server.py reads this env var
export API_KEY="dev-secret"
export PORT="8321"

python3 server.py
```

Then point Claude Code at it the same way as the packaged version:

```
claude mcp add kvasir-dev \
  --transport sse http://localhost:8321/sse \
  --header "Authorization: Bearer dev-secret"
```

Because `HA_URL` defaults to `http://supervisor/core` (only reachable
from inside an add-on container), you must override it to
`http://homeassistant:8123` for local runs, and use a manually-generated
long-lived token in place of the Supervisor-injected one.

## Building the Docker image locally

Requires the HA builder image (`ghcr.io/home-assistant/amd64-builder`), or
just use plain `docker build` with a `BUILD_FROM` arg matching your arch
from `build.yaml`:

```bash
cd kvasir
docker build --build-arg BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.19 -t kvasir-test .
docker run --rm -p 8321:8321 \
  -e API_KEY=dev-secret \
  -e HA_URL=http://host.docker.internal:8123 \
  -e SUPERVISOR_TOKEN=<token> \
  -e PORT=8321 \
  kvasir-test
```

## Deploying changes to the running add-on

1. Bump `version` in `kvasir/config.yaml` (Supervisor won't offer a
   rebuild otherwise).
2. Copy the updated folder back to `/addons/local/kvasir/` (see README
   Option A).
3. In HA: **Settings → Add-ons → Kvasir → Rebuild**, then **Restart**.

## Regression-testing the MCP tools

See [`evals/promptfoo/README.md`](evals/promptfoo/README.md) — runs
[promptfoo](https://www.promptfoo.dev/) against a live kvasir instance to
catch tool-calling regressions (bad JSON, broken validation, etc.) without
touching a real Home Assistant entity.

## Useful references

- Home Assistant add-on development docs: developers.home-assistant.io
  → "Add-ons" section (tutorial, configuration schema, bashio).
- `update` domain services: `update.install`, `update.skip`,
  `update.clear_skipped`.
- MCP Python SDK (`FastMCP`, SSE transport): the `mcp` PyPI package this
  project depends on.
