# Date

2026-04-02

# Status

* **Completed**

  * Deterministic single-action control loop was extended and tightened.
  * Stub and Factorio execution paths were normalized around executor-owned post-execution observation.
  * Movement transition artifact and terminal trace artifact were added and verified.
  * Factorio path now defaults to adapter-fed state instead of fixture-fed state.
  * Seed identity and starting position were introduced into normalized world-state contracts and visible terminal trace output.
  * A replay demo helper was added that runs the same Factorio-seeded path twice and compares outcomes.
* **Verified**

  * Full test suite passed at end of session.
  * Manual smoke checks produced expected terminal trace output.
  * Manual replay smoke check returned `True True True` for summary, trace event, and movement transition equality across same-seed runs.
* **In progress**

  * Transition from adapter-backed controlled stub into actual live Factorio state ingestion.
* **Deferred**

  * Real game/API integration for live player position and restart/reload.
  * Multi-step live gameplay loop beyond the single bounded action demo.
  * Any broader refactor toward `the_director.py` naming convention.

# Session scope

This session focused on turning the existing MK1 single-action pipeline into a more showable deterministic demo while preserving architecture boundaries. Work stayed within:

* contracts
* executors
* adapter seam
* runner/director
* artifact emission
* pipeline and contract tests

This session did **not** implement a live Factorio API connection.

# Objective

Advance the MK1 Factorio demo from “deterministic architecture with artifacts” toward “showable deterministic behavior,” specifically by:

* making post-execution behavior visible
* surfacing run identity in terminal output
* threading seed/start-state identity through the system
* proving replayability for same-seed runs in the current controlled Factorio adapter path

# Completed work

## Completed

### 1) Post-execution observation contract cleanup

Implemented a typed post-execution observation seam:

* `StubObservationUnavailable`
* `PostExecutionObservation` type alias

This replaced the prior asymmetry where the stub path returned a raw dict while the Factorio path returned a typed `Position`.

### 2) Stub executor alignment

Updated `StubActionExecutor.observe_player_position()` to return `StubObservationUnavailable` instead of a raw dict.

### 3) Runner typing/serialization cleanup

Updated `director/run_single_action.py` so post-execution observation is treated as an explicit typed contract and serialized consistently for returned payloads and JSON artifacts.

### 4) Stateful Factorio adapter behavior

Updated `FactorioClient` so `move_to(...)` mutates player position and `get_player_position()` reflects the moved-to position rather than always returning `(0.0, 0.0)`.

### 5) Movement transition artifact

Added a typed movement transition artifact:

* before position
* requested target position
* after position

Persisted it as `movement_transition.json` and returned it from the runner.

### 6) Terminal trace artifact

Added:

* `TerminalTraceEvent`
* `TerminalTraceArtifact`

Then extended the runner and artifact writer so terminal trace is:

* persisted as `terminal_trace.json`
* returned from the runner
* optionally emitted to stdout

### 7) Terminal trace display fields

Extended `TerminalTraceArtifact` to include:

* `title`
* `mode`
* `summary`

These are now populated by the runner and verified in tests.

### 8) Optional terminal emission

Added `emit_terminal_trace: bool = False` to `run_single_action(...)` and `_emit_terminal_trace(...)` to print the structured trace when enabled.

### 9) World session contract

Extended normalized world-state contract to include:

* `WorldSessionState`
* `seed`
* `starting_position`

Added `world_session` to `WorldState`.

### 10) Fixture identity threading

Updated the fixture world state to include:

* `world_session.seed`
* `world_session.starting_position`

### 11) Visible seed identity in trace

Updated terminal trace summary and `state_normalization` payload to include:

* seed
* starting position

### 12) Factorio adapter-fed state by default

Changed `run_single_action(...)` so:

* `stub` mode still defaults to fixture-fed state
* `factorio` mode now defaults to adapter-fed state via `FactorioClient.get_world_state_snapshot()`

### 13) Explicit Factorio seed override

Added `factorio_seed: str | None = None` to `run_single_action(...)` and threaded it through adapter initialization.

### 14) Replay-oriented adapter helper

Added `FactorioClient.restart_from_seed(...)` returning a fresh snapshot after reset.

### 15) Replay demo helper

Added `run_seed_replay_demo(...)` that runs the same seeded Factorio path twice and returns:

* `first_run`
* `second_run`
* `matching_summary`
* `matching_trace_events`
* `matching_movement_transition`

# Verified behavior

## Verified

### Automated

* Full suite passed after final changes.
* Pipeline tests verify:

  * stub and Factorio single-action paths
  * movement transition artifact
  * terminal trace artifact
  * terminal trace header fields
  * seed/start identity in trace payload
  * Factorio seed override path
  * replay demo same-seed equivalence

### Manual

* Manual terminal trace smoke output showed:

  * title
  * summary
  * ordered events
  * payloads
  * movement transition
* Manual replay smoke check returned:

  * `matching_summary == True`
  * `matching_trace_events == True`
  * `matching_movement_transition == True`

## Implemented but not separately verified beyond current scope

* `restart_from_seed(...)` exists on `FactorioClient`, but there was no separate dedicated test file added specifically for that method alone.
* The adapter-fed Factorio path is still internally controlled/stubbed, not live-game verified.

# Files or modules touched

## Contracts

* `contracts/artifacts.py`
* `contracts/world_state.py`

## Executors

* `executors/stub_action_executor.py`
* `executors/factorio_move_executor.py` (test path and behavior validation touched around its seam)

## Adapter

* `integrations/factorio/factorio_client.py`

## Director

* `director/run_single_action.py`

## Artifact writing

* `artifacts/run_artifact_writer.py`

## Fixtures

* `fixtures/mock_world_state.json`

## Tests

* `tests/test_stub_action_executor.py`
* `tests/test_factorio_move_executor_contract.py`
* `tests/test_run_single_action_pipeline.py`
* `tests/test_contract_validation.py`

# Important implementation details

## Architecture / ownership / boundaries (preserve exactly)

### Preserved invariants

* Deterministic control flow
* Executor-owned action execution
* Executor-owned post-execution observation
* Director remains thin orchestration, not agentic planner
* Typed contracts preferred over ad hoc dicts
* Artifacts remain first-class outputs
* Stub path remains valid deterministic harness for testing/regression

### Explicit boundaries

* **Director**

  * orchestrates normalization, validation, execution, observation, artifact writing
  * now also supports optional terminal trace emission
  * now supports seeded replay helper
* **Executors**

  * own execution and post-execution observation
* **Factorio adapter**

  * owns Factorio-facing runtime/session seam
  * now owns seed, starting position, reset/restart, and adapter-fed world snapshot
* **Fixture path**

  * remains the control/test harness
  * should not be removed
* **Factorio path**

  * should now be considered the demo-facing path
  * is adapter-fed by default
  * is still not live API/game integrated

## Important implementation behavior

* `run_single_action(...)` now accepts:

  * `emit_terminal_trace`
  * `factorio_seed`
* `run_seed_replay_demo(...)` exists and compares same-seed runs.
* `TerminalTraceArtifact.summary` now includes the seed.
* `state_normalization` terminal trace payload includes:

  * `tick`
  * `seed`
  * `starting_position`

# Current system state

## Verified current state

The system now supports a credible deterministic demo slice with:

* bounded single action
* explicit validation
* adapter-based execution
* observed after-state
* movement transition artifact
* terminal trace artifact
* visible seed/start-state identity
* same-seed replay check at the current controlled Factorio adapter level

## In progress

The next transition is from:

* adapter-fed controlled stub state

to:

* actual live Factorio state ingestion / live session control

## Deferred

* true live game read path
* true live restart/reload hook
* multi-step repeated gameplay loop
* real-world seed replay against an actual game session

# Known issues / remaining work

## Known limitations

* The Factorio adapter is still a controlled stub, not a live game API bridge.
* `get_world_state_snapshot()` returns a fixed schema with controlled values.
* Replay proof is real for the current adapter-fed path, but not yet proven against a live game session.
* Current demo is strongest as a deterministic control-loop demo, not yet a full live-play demo.

## Remaining work

1. Add a real live-state read path in `FactorioClient`

   * at minimum actual current player position
   * ideally seed/session metadata if available
2. Add a real restart/reload hook for the same world/seed
3. Keep stub path intact for tests
4. Drive live Factorio demo through the adapter seam rather than fixtures
5. Expand from single bounded action to repeated bounded loop once live read/restart exists

# Recommended next step

## Recommended next step

Implement the **first live Factorio bridge** in `integrations/factorio/factorio_client.py`.

The smallest worthwhile live slice is:

* read actual current player position from the game
* keep the rest of world snapshot temporarily controlled if needed
* feed that into the existing Factorio demo path
* preserve current stub and tests

That is the right next move because it advances the show path without collapsing the deterministic harness.
