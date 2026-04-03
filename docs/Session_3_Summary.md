# Title

Factorio Live Bridge Session Artifact (Mod-Backed RCON Bridge + Startup Hardening)

## Date

2026-04-03

## Status

- **completed**
  - Live Factorio bridge established for position read and bounded movement write
  - Mod-backed command ingress implemented for position read and move start
  - Shared RCON Python helper module added and raw transport scripts refactored to use it
  - Headless server start/stop/env helper scripts created
  - Bridge environment validator created
  - Live smoke and live guarded pytest both passed
- **verified**
  - Headless server can be started in a separate Proton compat path
  - Normal client can connect to the headless server
  - Live position reads return actual player coordinates
  - Live bounded movement updates player position in-game
  - `scripts/smoke_live_bridge.py` runs successfully against the live bridge
  - `tests/test_live_factorio_bridge_manual.py` passes when explicitly enabled
- **in progress**
  - Shell helper hardening and workflow cleanup were still being iterated during the session
  - No bounded multi-step “walk all the way to target” driver was implemented yet
- **deferred**
  - Higher-level movement logic beyond one bounded step per move command
  - Any change to director/executor behavior beyond current live adapter seam
  - Any broadening of live world-state ingestion beyond current player-position bridge

## Session scope

This session focused on converting the existing deterministic/stubbed Factorio demo path into a live bridge that reads actual player position from a running Factorio server/client setup and performs bounded live movement writes while preserving the established architecture:

- keep director thin
- keep executor-owned observation
- keep adapter ownership of live integration
- keep stub/test harness intact
- no agentic behavior
- no LLM behavior

## Objective

Implement the first live Factorio bridge so the demo path uses actual current player position from the running game instead of only controlled stub state, then harden the workflow enough that the bridge is repeatable and continuation-ready.

## Completed work

1. **Live read seam added and verified**
   - `FactorioClient` already had env-driven live command seams for position probing and move execution in the repo state used during this session.
   - Live position read was proven end-to-end through:
     - `scripts/get_player_position_rcon.py`
     - `scripts/get_player_position.py`
     - `FactorioClient.get_player_position()`

2. **Raw RCON bridge established**
   - Local RCON transport implemented and proven against a headless server running through Proton.
   - Headless server runs in a separate compat path to allow simultaneous normal client + headless server.
   - Server-side output uses `script-output/chatgpt/...`.

3. **Mod-backed ingress implemented**
   - Local mod created:
     - `factorio_mods/chatgpt_bridge_0.1.0/info.json`
     - `factorio_mods/chatgpt_bridge_0.1.0/control.lua`
   - Custom commands implemented:
     - `/chatgpt-get-position`
     - `/chatgpt-move-step`
     - `/chatgpt-stop-walk`
   - Read and move transport scripts were moved off raw `/c` ingress onto mod-backed commands.

4. **Bounded live movement implemented**
   - `scripts/move_to_rcon.py` issues one bounded walking step toward target coordinates and then stops walking.
   - Movement is directional and bounded by `FACTORIO_WALK_STEP_SECONDS`.
   - This is not full navigation/pathfinding.

5. **Shared RCON helper module added**
   - `scripts/factorio_rcon_common.py` created.
   - Common RCON socket/auth/command execution logic moved into shared helper.
   - `scripts/get_player_position_rcon.py` and `scripts/move_to_rcon.py` were refactored to use the shared helper.

6. **Operational scripts added**
   - `scripts/start_factorio_headless.sh`
   - `scripts/stop_factorio_headless.sh`
   - `scripts/set_factorio_bridge_env.sh`
   - `scripts/factorio_bridge_config.sh`
   - `scripts/check_factorio_bridge_env.py`

7. **Repo-owned validation / demo scripts added**
   - `scripts/smoke_live_bridge.py`
   - `scripts/run_live_factorio_demo.py`

8. **Guarded live pytest added and passed**
   - `tests/test_live_factorio_bridge_manual.py`
   - Explicitly guarded behind `RUN_LIVE_FACTORIO_TESTS=1`

## Verified behavior

The following behaviors were actually verified during the session:

- Headless Factorio server can be launched using Proton in a separate compat path.
- RCON listens on `127.0.0.1:27015`.
- Normal client can connect to the headless server via `127.0.0.1:34197`.
- `scripts/get_player_position_rcon.py` returned live JSON position from the real running game.
- `scripts/get_player_position.py` returned normalized live JSON position.
- `scripts/move_to_rcon.py` moved the player in the live game.
- `scripts/smoke_live_bridge.py` produced a successful before/move/after delta summary against the live bridge.
- `scripts/run_live_factorio_demo.py` ran successfully using `FactorioClient`.
- `tests/test_live_factorio_bridge_manual.py` passed with:
  - `RUN_LIVE_FACTORIO_TESTS=1 pytest -q tests/test_live_factorio_bridge_manual.py`

## Files or modules touched

### Live integration / adapter
- `integrations/factorio/factorio_client.py`

### Raw transport scripts
- `scripts/get_player_position.py`
- `scripts/get_player_position_rcon.py`
- `scripts/move_to_rcon.py`
- `scripts/factorio_rcon_common.py`

### Live workflow / validation scripts
- `scripts/smoke_live_bridge.py`
- `scripts/run_live_factorio_demo.py`
- `scripts/check_factorio_bridge_env.py`
- `scripts/start_factorio_headless.sh`
- `scripts/stop_factorio_headless.sh`
- `scripts/set_factorio_bridge_env.sh`
- `scripts/factorio_bridge_config.sh`

### Mod
- `factorio_mods/chatgpt_bridge_0.1.0/info.json`
- `factorio_mods/chatgpt_bridge_0.1.0/control.lua`

### Tests
- `tests/test_factorio_client_live_bridge.py`
- `tests/test_live_factorio_bridge_manual.py`

### Documentation
- `docs/live_factorio_bridge.md`

## Important implementation details

- The server must run in a separate Proton compat path:
  - `~/factorio-server-compat`
- The normal client and headless server are separate runtimes.
- The bridge must read/write against the **server** Factorio user-data directory, not the default client compat path.
- Key environment variables for live bridge operation:
  - `FACTORIO_RCON_HOST`
  - `FACTORIO_RCON_PORT`
  - `FACTORIO_RCON_PASSWORD`
  - `FACTORIO_USER_DATA_DIR`
  - `FACTORIO_POSITION_COMMAND`
  - `FACTORIO_RAW_POSITION_COMMAND`
  - `FACTORIO_MOVE_TO_COMMAND`
  - `FACTORIO_WALK_STEP_SECONDS`
- `scripts/check_factorio_bridge_env.py` now provides a JSON pass/fail summary of bridge readiness.
- `scripts/start_factorio_headless.sh` was hardened to run bridge validation after startup.
- `scripts/set_factorio_bridge_env.sh` needed an explicit fix for sourcing under zsh so it could correctly locate `scripts/factorio_bridge_config.sh`.
- Movement is currently **one bounded walking step**, not a full walk-to-target loop.
- The live pytest is intentionally opt-in and should stay that way.

## Current system state

- The live Factorio bridge is operational.
- Startup, shutdown, and environment loading scripts exist and were functioning by the end of the session.
- The environment validator reported `overall_ok: true` when the bridge was correctly loaded.
- Live read, live move, smoke, live demo, and guarded live pytest were all running as intended by the end of the session.

## Known issues / remaining work

- No multi-step bounded “walk to target until tolerance” driver has been implemented yet.
- No decision was made to move higher-level live movement logic into the director/executor path.
- The current movement behavior is still a single bounded step per command, which means many distant targets can produce similar initial movement.
- This is correct for the current boundary-preserving design, but it is still limited behaviorally.
- Shell helper behavior required zsh-specific handling during this session; future edits to shell scripts should be tested from the actual shell used.
- No new broad live world-state snapshot beyond player position was implemented.

## Recommended next step

Implement a repo-owned bounded multi-step live movement driver script (not director logic yet), e.g. `scripts/run_live_factorio_walk_to_target.py`, that:

- accepts target `x y`
- uses `FactorioClient`
- repeatedly issues bounded live move steps
- re-observes position after each step
- stops on:
  - tolerance reached
  - max steps reached
  - no progress / stuck detection

This is the next best logic step because it builds on the verified live adapter path without polluting architecture boundaries prematurely.

## Safe stopping point

This session ended at a safe stopping point.

The bridge is not merely implemented; it is also operationally repeatable:

- server startup works
- env loading works
- validation works
- client connect works
- smoke works
- live adapter demo works
- guarded live pytest works

No additional patch is required just to preserve the working state reached in this session.

## Resume instruction

On resume, assume the current live bridge is working and do **not** re-debug startup unless the validator fails.

First:
1. `bash scripts/start_factorio_headless.sh`
2. `source scripts/set_factorio_bridge_env.sh`
3. `python scripts/check_factorio_bridge_env.py`

If `overall_ok` is true, proceed directly to the next logic task instead of re-opening transport/setup debugging.

## Recommended filename

`session_artifact_factorio_live_bridge_2026-04-03.md`

## Bottom line

This session successfully converted the Factorio demo path from a mostly stubbed live-in-name-only bridge into a real, mod-backed, repeatable live integration. The system can now start a separate headless server, connect a normal client, read actual player position, perform bounded walking movement, validate its own environment, run smoke checks, run a live adapter demo, and pass an opt-in live pytest. The next step is no longer setup rescue; it is bounded movement logic built on top of a verified live adapter seam.

## Copy-paste continuation prompt for the next chat

Current state:
- live Factorio bridge is operational and verified
- mod-backed command ingress is in place
- startup/shutdown/env/validation scripts exist and were working at the end of the last session
- smoke script, live adapter demo, and guarded live pytest all passed
- architecture boundaries must remain unchanged:
  - director thin
  - executor-owned observation
  - adapter owns live integration
  - stub harness intact
  - no agentic behavior
  - no LLM behavior

Next objective:
Implement a bounded multi-step live movement driver script (not director logic yet), likely `scripts/run_live_factorio_walk_to_target.py`, that uses `FactorioClient` to repeatedly step toward a target until tolerance, max-steps, or no-progress/stuck detection.

Constraints:
- provide exact code patches with correct indentation
- do not guess
- preserve architecture boundaries exactly
- only claim behavior that is actually verified
