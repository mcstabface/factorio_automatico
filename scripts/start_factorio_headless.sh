#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/factorio_bridge_config.sh"

echo "Checking Factorio headless prerequisites..."

if [[ ! -f "${PROTON_PATH}" ]]; then
  echo "Missing Proton launcher: ${PROTON_PATH}" >&2
  exit 1
fi

if [[ ! -f "${FACTORIO_EXE}" ]]; then
  echo "Missing Factorio executable: ${FACTORIO_EXE}" >&2
  exit 1
fi

if [[ ! -f "${SAVE_PATH}" ]]; then
  echo "Missing save file: ${SAVE_PATH}" >&2
  exit 1
fi

if [[ ! -d "${SERVER_MOD_PATH}" ]]; then
  echo "Missing server mod directory: ${SERVER_MOD_PATH}" >&2
  echo "Copy factorio_mods/chatgpt_bridge_0.1.0 into the server mods directory first." >&2
  exit 1
fi

if ss -ltn | grep -q "${RCON_HOST}:${RCON_PORT}"; then
  echo "RCON port ${RCON_HOST}:${RCON_PORT} is already listening." >&2
  echo "A headless server may already be running." >&2
  exit 1
fi

mkdir -p "${SERVER_COMPAT_PATH}"

echo
echo "Starting Factorio headless server..."
echo "Save: ${SAVE_PATH}"
echo "Server compat path: ${SERVER_COMPAT_PATH}"
echo "RCON: ${RCON_HOST}:${RCON_PORT}"
echo

STEAM_COMPAT_CLIENT_INSTALL_PATH="${STEAM_ROOT}" \
STEAM_COMPAT_DATA_PATH="${SERVER_COMPAT_PATH}" \
SteamAppId=427520 \
"${PROTON_PATH}" run \
"${FACTORIO_EXE}" \
--start-server "${SAVE_PATH}" \
--rcon-bind "${RCON_HOST}:${RCON_PORT}" \
--rcon-password "${RCON_PASSWORD}" &

SERVER_PID=$!

sleep 2

if ! ps -p "${SERVER_PID}" > /dev/null 2>&1; then
  echo "Headless server process did not stay running." >&2
  exit 1
fi

echo "Headless server launched with PID ${SERVER_PID}."
echo

echo "Waiting for RCON to accept connections..."
RCON_READY=0
for _ in {1..20}; do
  if python - <<PY
import socket
import sys

sock = socket.socket()
sock.settimeout(0.5)
try:
    sock.connect(("${RCON_HOST}", int("${RCON_PORT}")))
except OSError:
    sys.exit(1)
else:
    sys.exit(0)
finally:
    sock.close()
PY
  then
    RCON_READY=1
    break
  fi

  sleep 0.5
done

if [[ "${RCON_READY}" -ne 1 ]]; then
  echo "RCON did not become ready on ${RCON_HOST}:${RCON_PORT}." >&2
  exit 1
fi

export FACTORIO_RCON_HOST="${RCON_HOST}"
export FACTORIO_RCON_PORT="${RCON_PORT}"
export FACTORIO_RCON_PASSWORD="${RCON_PASSWORD}"
export FACTORIO_USER_DATA_DIR="${SERVER_FACTORIO_DIR}"
export FACTORIO_POSITION_COMMAND="${FACTORIO_POSITION_COMMAND}"
export FACTORIO_RAW_POSITION_COMMAND="${FACTORIO_RAW_POSITION_COMMAND}"
export FACTORIO_MOVE_TO_COMMAND="${FACTORIO_MOVE_TO_COMMAND}"
export FACTORIO_WALK_STEP_SECONDS="${FACTORIO_WALK_STEP_SECONDS}"

echo "Bridge environment validation:"
python scripts/check_factorio_bridge_env.py || {
  echo "Bridge environment validation failed." >&2
  exit 1
}

echo
echo "Client connect address:"
echo "  ${CLIENT_CONNECT_ADDRESS}"
echo
echo "In another terminal, run:"
echo "  source scripts/set_factorio_bridge_env.sh"
echo
echo "Then test:"
echo "  python scripts/get_player_position_rcon.py"
echo "  python scripts/smoke_live_bridge.py"
echo "  python scripts/run_live_factorio_demo.py"