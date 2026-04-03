# Live Factorio Bridge Runbook

## Purpose

This runbook documents the current live bridge workflow for the Factorio demo path.

Current live bridge scope:

- live player position read
- live bounded move step write
- repo-owned startup, env, validation, and smoke helpers
- repo-owned bounded multi-step walk driver
- deterministic fallback remains available when live commands are not configured

This runbook does **not** describe a full autonomous gameplay loop.

---

## Architecture boundaries

Preserve these boundaries exactly:

- Director remains thin
- Executor owns execution and post-execution observation
- Factorio adapter owns the live integration seam
- Repo-owned wrapper scripts own normalization and bounded workflow logic
- Raw RCON scripts own transport details
- Stub path remains intact for deterministic regression testing

The live bridge is intentionally narrow.
Do not move higher-level planning into the Director through “just one more helper.”
That is how small bridges turn into haunted houses.

---

## Current script layers

### Adapter layer

The adapter owns the live-facing seam:

- `integrations/factorio/factorio_client.py`

Current adapter surface includes:

- `get_player_position()`
- `get_world_state_snapshot()`
- `move_to(x, y)`
- `restart_from_seed(...)`

### Repo-owned wrapper and workflow layer

These files are repo-owned workflow helpers built on top of the adapter and transport seam:

- `scripts/get_player_position.py`
- `scripts/run_live_factorio_demo.py`
- `scripts/smoke_live_bridge.py`
- `scripts/run_live_factorio_walk_to_target.py`
- `scripts/check_factorio_bridge_env.py`
- `scripts/start_factorio_headless.sh`
- `scripts/stop_factorio_headless.sh`
- `scripts/set_factorio_bridge_env.sh`
- `scripts/factorio_bridge_config.sh`

### Raw transport layer

These files own the RCON command transport details:

- `scripts/get_player_position_rcon.py`
- `scripts/move_to_rcon.py`
- `scripts/factorio_rcon_common.py`

### Mod layer

Custom commands are provided by the local mod:

- `factorio_mods/chatgpt_bridge_0.1.0/info.json`
- `factorio_mods/chatgpt_bridge_0.1.0/control.lua`

Current commands:

- `/chatgpt-get-position`
- `/chatgpt-move-step x,y`
- `/chatgpt-stop-walk`

---

## Current live behaviors

### Position read

Live position read flows through:

- `scripts/get_player_position_rcon.py`
- `scripts/get_player_position.py`
- `FactorioClient.get_player_position()`

### Single bounded move write

Single bounded move write flows through:

- `scripts/move_to_rcon.py`
- `FactorioClient.move_to(x, y)`

This is one bounded walking step.
It is not pathfinding.
It is not a full walk loop.

### Repo-owned multi-step walk driver

Multi-step bounded walking now exists as repo-owned logic:

- `scripts/run_live_factorio_walk_to_target.py`

This driver:

- accepts target `x y`
- uses `FactorioClient`
- repeatedly issues bounded move steps toward the target
- re-observes player position after each step
- stops on:
  - already within tolerance
  - target reached
  - max steps reached
  - stuck / no progress detected

This logic is intentionally kept **outside** the Director and executor contracts.

---

## Preconditions

The current bridge assumes:

- Steam-installed Factorio Windows build running through Proton
- a normal Factorio client instance
- a separate headless/server instance launched through a separate Proton compat path
- RCON enabled on the headless/server instance
- the normal client connected to that headless/server instance
- the user is in-world with at least one connected player visible to the server

---

## Save path

Current observed save path example:

- `~/.local/share/Steam/steamapps/compatdata/427520/pfx/drive_c/users/steamuser/AppData/Roaming/Factorio/saves/Here_we_go.zip`

Adjust this if your save path differs.

---

## Environment variables

Important live bridge environment variables:

- `FACTORIO_RCON_HOST`
- `FACTORIO_RCON_PORT`
- `FACTORIO_RCON_PASSWORD`
- `FACTORIO_USER_DATA_DIR`
- `FACTORIO_POSITION_COMMAND`
- `FACTORIO_RAW_POSITION_COMMAND`
- `FACTORIO_MOVE_TO_COMMAND`
- `FACTORIO_WALK_STEP_SECONDS`

These are expected to be set by:

- `scripts/set_factorio_bridge_env.sh`

Do not hand-edit downstream scripts every time something moves.
That is a reliable way to create fake progress.

---

## Launch flow

### Start the headless/server instance

Use the repo helper:

```bash id="v6j3sq"
bash scripts/start_factorio_headless.sh