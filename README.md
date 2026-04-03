# Factorio Modular Expert System

A deterministic, non-agentic Modular Expert System for Factorio.

This repo is a **bounded architecture demo with a live bridge**.
It shows how a narrow expert system can:

- observe Factorio state through explicit contracts
- validate legal actions before execution
- route execution through explicit executor paths
- persist artifacts for replay and inspection
- drive a verified live movement seam without turning into an opaque agent

It is **not** a production bot.
It is **not** an autonomous agent framework.
It is **not** an LLM-driven controller.

The point is to make the architecture visible and auditable.

---

## Core Principles

This repo follows a few hard rules:

- deterministic, auditable behavior
- modular experts with narrow contracts
- explicit orchestration
- artifacts as first-class outputs
- no hidden state
- no implicit tool chaining
- capability growth through more bounded experts, not more autonomy

The Director stays dumb on purpose.
Experts do the bounded work.
Artifacts tell the story.

---

## Current Repo State

Today, the repo has two related slices:

1. a deterministic single-action MES demo pipeline
2. a verified live Factorio bridge for player-position read and bounded movement write

That means the project now demonstrates both:

- **control-plane architecture**
- **live integration through a thin adapter seam**

The live slice is still intentionally narrow.
It is not a full gameplay loop.

---

## Current Demo Slice

The current deterministic pipeline can:

1. load or acquire world state
2. normalize and validate state
3. validate a bounded action
4. execute through an explicit executor path
5. observe post-execution state through the executor seam
6. persist artifacts for inspection

Current bounded demo action:

- `MOVE_TO`

Current executor paths:

- `stub`
- `factorio`

The `stub` executor proves the architecture.
The `factorio` executor proves the adapter seam.

---

## Live Bridge Slice

The repo also includes a live Factorio bridge with verified scope for:

- live player position read
- bounded live movement write
- repo-owned startup, env, validation, and smoke scripts
- guarded live pytest coverage
- bounded multi-step walk-to-target driver script

Current live behavior is intentionally narrow:

- observe actual player position
- issue one bounded move step
- optionally repeat bounded steps in a repo-owned driver script
- stop based on explicit termination rules

This is **not** pathfinding.
This is **not** autonomous play.
This is **not** hidden planning logic.

---

## Current Structure

- `contracts/`
  - typed contracts for state, actions, execution results, audits, and debug artifacts
- `validation/`
  - deterministic validators for state and actions
- `experts/`
  - bounded experts for state normalization and action validation
- `executors/`
  - explicit execution paths (`stub` and `factorio`)
- `integrations/factorio/`
  - thin Factorio adapter seam
- `director/`
  - thin orchestration runner
- `artifacts/`
  - artifact writing support
- `fixtures/`
  - sample state used for deterministic demo runs
- `scripts/`
  - repo-owned operational, smoke, and live bridge helpers
- `factorio_mods/`
  - local mod used for bridge commands
- `tests/`
  - contract, pipeline, bridge, and guarded live tests
- `docs/`
  - runbooks and session artifacts

---

## What Exists Right Now

### Contracts

The repo currently has typed contracts for:

- normalized world state
- world session identity
- legal actions
- expert debug artifacts
- execution results
- movement transition artifacts
- terminal trace artifacts
- run audit output

### Validation

The system currently validates:

- state shape
- action legality
- movement target shape
- resource mining target shape
- entity interaction identity
- craftability / placeability checks

### Experts

Current bounded experts:

- `StateNormalizationExpert`
- `ActionValidationExpert`

### Executors

Current execution paths:

- `StubActionExecutor`
- `FactorioMoveExecutor`

### Adapter

Current Factorio adapter surface includes:

- `get_player_position()`
- `get_world_state_snapshot()`
- `move_to(x, y)`
- `restart_from_seed(...)`

### Artifacts

The current pipeline writes and/or returns artifacts such as:

- input state snapshot
- state normalization debug
- validated action
- action validation debug
- execution result
- run audit
- movement transition
- terminal trace

---

## Live Bridge Files

Important live bridge files include:

### Adapter

- `integrations/factorio/factorio_client.py`

### Transport and wrappers

- `scripts/get_player_position.py`
- `scripts/get_player_position_rcon.py`
- `scripts/move_to_rcon.py`
- `scripts/factorio_rcon_common.py`

### Workflow helpers

- `scripts/start_factorio_headless.sh`
- `scripts/stop_factorio_headless.sh`
- `scripts/set_factorio_bridge_env.sh`
- `scripts/factorio_bridge_config.sh`
- `scripts/check_factorio_bridge_env.py`

### Demo and smoke scripts

- `scripts/run_live_factorio_demo.py`
- `scripts/smoke_live_bridge.py`
- `scripts/run_live_factorio_walk_to_target.py`

### Mod

- `factorio_mods/chatgpt_bridge_0.1.0/info.json`
- `factorio_mods/chatgpt_bridge_0.1.0/control.lua`

### Tests

- `tests/test_factorio_client_live_bridge.py`
- `tests/test_run_live_factorio_walk_to_target.py`
- `tests/test_live_factorio_bridge_manual.py`

---

## Multi-Step Walk Driver

The repo-owned multi-step walk driver is:

- `scripts/run_live_factorio_walk_to_target.py`

It uses the existing `FactorioClient` seam and repeatedly issues bounded move steps toward a target.

It stops on one of these conditions:

- already within tolerance
- target reached
- max steps reached
- stuck / no progress detected

Example:

```bash
python scripts/run_live_factorio_walk_to_target.py 10 10

Optional arguments:

python scripts/run_live_factorio_walk_to_target.py <x> <y> [tolerance] [max_steps] [min_progress]

This script is intentionally repo-owned logic only.
It does not move planning into the Director or widen the executor contract.

Live Bridge Workflow

From the repo root, the normal resume flow is:

bash scripts/start_factorio_headless.sh
source scripts/set_factorio_bridge_env.sh
python scripts/check_factorio_bridge_env.py

If the validator reports success, you can then run:

python scripts/smoke_live_bridge.py
python scripts/run_live_factorio_demo.py
python scripts/run_live_factorio_walk_to_target.py 10 10

For more detail, see:

docs/live_factorio_bridge.md
Running Tests

From the repo root:

pytest -q

Deterministic coverage for the walk driver:

pytest -q tests/test_run_live_factorio_walk_to_target.py

Guarded live bridge tests:

RUN_LIVE_FACTORIO_TESTS=1 pytest -q tests/test_live_factorio_bridge_manual.py

The live tests are intentionally opt-in.

What This Repo Is Trying To Show

This repo is trying to show that a game-playing system does not need to be an opaque “AI agent.”

You can build a clear architecture instead:

observe state through explicit contracts
validate actions before execution
keep reasoning bounded
route execution explicitly
persist artifacts for replay
keep each layer inspectable

For this project, that matters more than pretending to be human.

Current Limitations

Current limitations are deliberate:

live bridge scope is currently centered on player position and bounded movement
movement is step-based, not pathfinding
no broad live world-state ingestion beyond the current seam
no autonomous gameplay loop
no hidden planner
no widened director behavior
no production hardening beyond what supports the demo and live bridge workflow

That limitation is a feature here.
The architecture stays legible because the scope stays bounded.