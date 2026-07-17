#!/usr/bin/with-contenv bashio

export API_KEY
API_KEY="$(bashio::config 'api_key')"
export LOG_LEVEL
LOG_LEVEL="$(bashio::config 'log_level')"
export PORT="8321"
export HA_URL="http://supervisor/core"

if [ -z "${API_KEY}" ]; then
    bashio::exit.nok "api_key is not set. Configure it in the add-on's Configuration tab before starting."
fi

bashio::log.info "Starting Kvasir MCP server on port ${PORT}"
exec python3 /app/server.py
