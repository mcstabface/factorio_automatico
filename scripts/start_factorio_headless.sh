#!/usr/bin/env bash
set -euo pipefail

STEAM_ROOT="${HOME}/.local/share/Steam"
PROTON_PATH="${STEAM_ROOT}/steamapps/common/Proton - Experimental/proton"
FACTORIO_EXE="${STEAM_ROOT}/steamapps/common/Factorio/bin/x64/factorio.exe"

CLIENT_COMPAT_PATH="${STEAM_ROOT}/steamapps/compatdata/427520"
SERVER_COMPAT_PATH="${HOME}/factorio-server-compat"

SAVE_PATH="${CLIENT_COMPAT_PATH}/pfx/drive_c/users/steamuser/AppData/Roaming/Factorio/saves/Here_we_go.zip"
SERVER_FACTORIO_DIR="${SERVER_COMPAT_PATH}/pfx/drive_c/users/steamuser/AppData/Roaming/Factorio"
SERVER_MOD_DIR="${SERVER_FACTORIO_DIR}/mods"
SERVER_MOD_PATH="${SERVER_MOD_DIR}/chatgpt_bridge_0.1.0"

RCON_HOST="127.0.0.1"
RCON_PORT="27015"
RCON_PASSWORD="stabby"
CLIENT_CONNECT_ADDRESS="127.0.0.1:34197"

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
echo "Client connect address:"
echo "  ${CLIENT_CONNECT_ADDRESS}"
echo
echo "In another terminal, run:"
echo "  source scripts/set_factorio_bridge_env.sh"
echo
echo "Then test:"
echo "  python scripts/get_player_position_rcon.py"
echo "  python scripts/smoke_live_bridge.py"