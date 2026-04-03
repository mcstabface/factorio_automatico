#!/usr/bin/env bash

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

FACTORIO_POSITION_COMMAND="python scripts/get_player_position.py"
FACTORIO_RAW_POSITION_COMMAND="python scripts/get_player_position_rcon.py"
FACTORIO_MOVE_TO_COMMAND="python scripts/move_to_rcon.py"
FACTORIO_WALK_STEP_SECONDS="0.25"