# Live Factorio Bridge Runbook

## Purpose

This runbook documents the current live bridge workflow for the Factorio demo path.

Current live bridge scope:

- live player position read
- live bounded move step write
- adapter-fed integration through repo-owned scripts
- deterministic fallback remains available when live commands are not configured

This runbook does **not** describe a full autonomous gameplay loop.

## Architecture boundaries

Preserve these boundaries exactly:

- Director remains thin
- Executor owns execution and post-execution observation
- Factorio adapter owns the live integration seam
- Repo-owned wrapper scripts own normalization
- Raw RCON scripts own transport details
- Stub path remains intact for deterministic regression testing

## Current script layers

## Current mod layer

Custom commands are provided by the local mod:

- `factorio_mods/chatgpt_bridge_0.1.0/info.json`
- `factorio_mods/chatgpt_bridge_0.1.0/control.lua`

Current commands:

- `/chatgpt-get-position`
- `/chatgpt-move-step x,y`

### Position read

- Wrapper:
  - `scripts/get_player_position.py`
- Raw transport:
  - `scripts/get_player_position_rcon.py`

### Move write

- Raw transport:
  - `scripts/move_to_rcon.py`

## Preconditions

The current bridge assumes:

- Steam-installed Factorio Windows build running through Proton
- a normal Factorio client instance
- a separate headless/server instance launched through a separate Proton compat path
- RCON enabled on the headless/server instance
- the normal client connected to that headless/server instance
- the user is in-world with at least one connected player visible to the server

## Save path

Current observed save path example:

- `~/.local/share/Steam/steamapps/compatdata/427520/pfx/drive_c/users/steamuser/AppData/Roaming/Factorio/saves/Here_we_go.zip`

## Launch the headless/server instance

Use a separate compat path so the normal client and server can coexist.

Example:

```bash
mkdir -p "$HOME/factorio-server-compat" && \
STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/.local/share/Steam" \
STEAM_COMPAT_DATA_PATH="$HOME/factorio-server-compat" \
SteamAppId=427520 \
"$HOME/.local/share/Steam/steamapps/common/Proton - Experimental/proton" run \
"$HOME/.local/share/Steam/steamapps/common/Factorio/bin/x64/factorio.exe" \
--start-server "$HOME/.local/share/Steam/steamapps/compatdata/427520/pfx/drive_c/users/steamuser/AppData/Roaming/Factorio/saves/Here_we_go.zip" \
--rcon-bind 127.0.0.1:27015 \
--rcon-password stabby