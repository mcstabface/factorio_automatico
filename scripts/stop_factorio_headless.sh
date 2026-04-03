#!/usr/bin/env bash
set -euo pipefail

MATCH_PATTERN='Factorio\\bin\\x64\\factorio.exe --start-server'
RCON_PORT="27015"

echo "Looking for running headless Factorio server processes..."

PIDS="$(ps -ef | grep -i 'Factorio\\bin\\x64\\factorio.exe --start-server' | grep -v grep | awk '{print $2}')"

if [[ -z "${PIDS}" ]]; then
  echo "No running headless Factorio server process found."
else
  echo "Stopping headless Factorio server PID(s): ${PIDS}"
  kill ${PIDS}

  sleep 2

  STILL_RUNNING="$(ps -ef | grep -i 'Factorio\\bin\\x64\\factorio.exe --start-server' | grep -v grep | awk '{print $2}' || true)"
  if [[ -n "${STILL_RUNNING}" ]]; then
    echo "Process still running after SIGTERM, forcing stop: ${STILL_RUNNING}"
    kill -9 ${STILL_RUNNING}
    sleep 1
  fi
fi

if ss -ltn | grep -q "127.0.0.1:${RCON_PORT}"; then
  echo "RCON port 127.0.0.1:${RCON_PORT} is still listening." >&2
  echo "Another process may still own the port." >&2
  exit 1
fi

echo "Headless Factorio server stopped."