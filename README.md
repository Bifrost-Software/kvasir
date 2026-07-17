# Kvasir

A Home Assistant **Add-on** that runs a small MCP (Model Context Protocol)
server alongside Home Assistant, exposing pending updates (`update.*`
entities — Core, Supervisor, OS, add-ons, HACS integrations) as tools an
MCP client can call: list them, install one, or skip one.

Part of **[Draupnir](https://bifrost-labs.atlassian.net/jira/software/projects/DRAUPNIR)**,
Bifrost's open-source initiative — public repos and community projects.
Tracked as an Epic in the Draupnir Jira project.

This exists because Home Assistant's own built-in MCP server
(`mcp_server` integration) only exposes intents from the Assist API, and
the `update` domain isn't part of that by default — there's no built-in
way to say "install my pending updates" through it. Kvasir is a second,
independent MCP endpoint that fills that specific gap.

## Why an add-on (and not a standalone script)

Home Assistant is installed here as **HAOS/Supervised** (confirmed via the
`hassio` component being present), so it supports Add-ons. Running as an
add-on instead of a script on a separate machine means:

- It starts/stops with Home Assistant — no dependency on this PC being on.
- It gets a scoped `SUPERVISOR_TOKEN` auto-injected by the Supervisor
  (via `homeassistant_api: true` / `hassio_api: true` in `config.yaml`) —
  no long-lived access token to generate, store, or rotate manually.
- It's visible and manageable from Settings → Add-ons like any other
  integration.

## Project layout

```
kvasir/
├── repository.yaml   # marks this repo as an HA add-on repository
└── kvasir/           # the add-on itself (slug: kvasir)
    ├── config.yaml    # add-on manifest: ports, options, API access
    ├── build.yaml     # base image per architecture
    ├── Dockerfile
    ├── run.sh         # bashio entrypoint, reads options, execs server.py
    ├── app/
    │   ├── server.py    # the MCP server (FastMCP + SSE + bearer auth)
    │   └── requirements.txt
    ├── README.md        # shown in the HA UI for this add-on
    └── CHANGELOG.md
```

## Installing into Home Assistant

Pick one:

### Option A — local add-on (fastest, no GitHub needed)

1. Copy the `kvasir/` (inner) folder onto the HA host, into
   `/addons/local/kvasir/`. Easiest ways to get files onto the host:
   - Install the official **Samba share** add-on, then copy the folder
     into the `addons` share.
   - Or install the **Terminal & SSH** add-on and `scp`/`rsync` it in.
2. In HA: **Settings → Add-ons → Add-on Store**, click the **⋮** menu top
   right → **Check for updates** (this rescans local add-ons). "Kvasir"
   should appear under **Local add-ons**.
3. Click it → **Install**.
4. Go to the **Configuration** tab, set `api_key` to a random secret
   (e.g. generate one with `openssl rand -hex 32`), save.
5. **Start** the add-on. Check the **Log** tab for
   `Listening on 0.0.0.0:8321`.

### Option B — as a git add-on repository

1. This repo (`Bifrost-Software/kvasir`, public) is already structured as
   an add-on repository via `repository.yaml`.
2. In HA: **Settings → Add-ons → Add-on Store → ⋮ → Repositories**, add
   `https://github.com/Bifrost-Software/kvasir`.
3. Install/configure/start as in Option A, steps 3–5.

## Connecting Claude Code

```
claude mcp add kvasir \
  --transport sse http://homeassistant:8321/sse \
  --header "Authorization: Bearer <api_key-from-config>"
```

Verify with `claude mcp get kvasir` — should show `✔ Connected`.

## Tools exposed

See [`kvasir/README.md`](kvasir/README.md) for the tool list and options
reference.

## Security notes

- `api_key` is a shared secret between this add-on and whatever MCP client
  connects to it (Claude Code here). Treat it like a password — don't
  commit it, don't paste it in chat transcripts. Rotate it by changing the
  option and restarting the add-on, then updating the client's registered
  header.
- The add-on only requests `homeassistant_api` / `hassio_api` access
  (needed to call `update.install`/`update.skip`), not full Supervisor
  admin rights.
- This repo is **public**. Never commit real `api_key` values, tokens, or
  any HA-instance-identifying secrets — configuration stays local to your
  HA install, not in this repo.

## Local development

See [`DEVELOPMENT.md`](DEVELOPMENT.md).
