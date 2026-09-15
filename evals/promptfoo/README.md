# promptfoo evals

Regression tests for kvasir's MCP tools (`list_pending_updates`, `install_update`,
`skip_update`), run against a live kvasir instance via promptfoo's [MCP
provider](https://www.promptfoo.dev/docs/providers/mcp/).

## Running

1. Start kvasir (packaged add-on, or locally per [`../../DEVELOPMENT.md`](../../DEVELOPMENT.md)).
2. Set the two env vars it needs — never commit real values:
   ```bash
   export KVASIR_MCP_URL="http://localhost:8321/sse"
   export KVASIR_API_KEY="dev-secret"
   ```
3. Run:
   ```bash
   npx promptfoo@latest eval -c evals/promptfoo/promptfooconfig.yaml
   ```

## What's covered, and what isn't

The suite only exercises the read-only tool (`list_pending_updates`) and the
input-validation paths of `install_update`/`skip_update` (a non-`update.*`
`entity_id` is rejected before any request reaches Home Assistant). It
deliberately does **not** call either tool with a real `update.*` entity,
because that would actually install or skip an update on whatever HA
instance `KVASIR_MCP_URL` points at — not something that should happen as a
side effect of running a test suite.

To verify the success paths, do it manually against a disposable/test HA
instance with a real pending update, not here.

Auth is also not covered by this config — promptfoo's `mcp` provider doesn't
expose a clean per-test header override, so verifying the bearer-auth check
in `BearerAuthMiddleware` (`../../kvasir/app/server.py`) is still a manual
`curl` check:
```bash
curl -i http://localhost:8321/sse -H "Authorization: Bearer wrong-token"  # expect 401
```
