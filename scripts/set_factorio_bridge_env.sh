#!/usr/bin/env bash

export FACTORIO_RCON_HOST="127.0.0.1"
export FACTORIO_RCON_PORT="27015"
export FACTORIO_RCON_PASSWORD="stabby"

export FACTORIO_USER_DATA_DIR="${HOME}/factorio-server-compat/pfx/drive_c/users/steamuser/AppData/Roaming/Factorio"

export FACTORIO_POSITION_COMMAND="python scripts/get_player_position.py"
export FACTORIO_RAW_POSITION_COMMAND="python scripts/get_player_position_rcon.py"
export FACTORIO_MOVE_TO_COMMAND="python scripts/move_to_rcon.py"

export FACTORIO_WALK_STEP_SECONDS="0.25"

echo "Factorio bridge environment loaded."
echo "FACTORIO_RCON_HOST=${FACTORIO_RCON_HOST}"
echo "FACTORIO_RCON_PORT=${FACTORIO_RCON_PORT}"
echo "FACTORIO_USER_DATA_DIR=${FACTORIO_USER_DATA_DIR}"