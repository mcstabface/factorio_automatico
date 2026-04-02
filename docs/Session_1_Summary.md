# Title

Factorio MES Session Artifact - Deterministic Demo Pipeline Checkpoint

## Recommended filename

`docs/session_artifact_factorio_mes_demo_pipeline_checkpoint_2026-04-02.md`

## Date

2026-04-02

## Status

- **completed**
  - deterministic contracts established for world state, actions, execution results, run audit, and expert debug artifacts
  - deterministic validators implemented for world state and action legality
  - thin single-action runner implemented
  - explicit executor selection implemented in runner (`stub` and `factorio`)
  - explicit `run_id` input implemented in runner
  - explicit `raw_state` input implemented in runner
  - explicit `candidate_action` input implemented in runner
  - `Action.move_to(...)` factory implemented
  - typed Factorio adapter seam restored (`MoveToCommandResult`, `Position`)
  - typed Factorio move executor aligned to typed adapter seam
  - stub executor aligned to typed execution-result contract
  - artifact writing path remains thin and deterministic
  - test coverage added across contracts, executors, factories, and pipeline

- **verified**
  - tests were repeatedly run throughout the session and passing states were reported by the user after fixes
  - a recent reported passing state included the full suite after correcting executor / adapter mismatches
  - multiple regressions caused by partial saves or stale test seams were identified and corrected during the session

- **in progress**
  - no live Factorio game-state ingestion
  - no live post-action world refresh / before-after comparison
  - no broader action set beyond the current bounded demo slice
  - no README had existed at the time it was requested; README text was drafted but file creation was not verified in-session

- **deferred**
  - broader expert set (planning, inventory reasoning, production reasoning, logistics, recovery)
  - visualization / UI layer
  - production-grade hardening beyond what was useful for the architecture demo
  - richer live adapter surface beyond the current movement seam

## Session scope

This session focused on building and tightening a **credible deterministic demo pipeline** for a Factorio Modular Expert System, while keeping architecture explicit and non-agentic.

The session started from the project brief and progressed through:
- contract creation and validation hardening
- runner/orchestration review
- action and world-state schema tightening
- debug artifact hardening
- execution-result formalization
- typed executor and adapter seams
- demo usability improvements in the runner
- targeted test additions and fixes

The goal was not production completeness. The goal was a trustworthy, inspectable demo architecture with visible execution seams.

## Objective

Build a deterministic, auditable, non-agentic Factorio MES demo that can:

1. accept normalized or raw state input
2. validate bounded actions against state
3. route execution explicitly through a chosen executor
4. persist artifacts for inspection
5. demonstrate the architecture clearly enough that others can follow progress

## Completed work

### 1. Core contracts implemented
Implemented typed contracts for:
- `WorldState` and related state substructures
- `Action` and `ActionType`
- `ExpertDebugArtifact`
- `ActionExecutionResult`
- `RunAudit`

### 2. World-state contract refined
Implemented / refined:
- stable `entity_id` on nearby entities
- nullable `Objective.current_goal`
- missing `objective` block allowed and normalized to `current_goal=None`

### 3. Action legality contract refined
Implemented / refined:
- `INTERACT_ENTITY` now validates `target_entity_id` instead of ambiguous `entity_name`
- `MINE_RESOURCE` now validates both `resource_name` and `target_position`
- validator coverage expanded for missing/malformed params

### 4. Debug artifact contract hardened
Added or confirmed:
- `success`
- `warnings`
- `error_message`
- `duration_ms`
- `input_ref`
- `output_ref`
- default-empty `proposed_actions`

### 5. Execution-result contract formalized
Implemented typed execution result with:
- `success`
- `executor_name`
- `action_id`
- `action_type`
- `execution_status`
- `target_position`
- `observed_result`
- `error_message`

### 6. Executor seams aligned
Implemented / aligned:
- `StubActionExecutor`
- `FactorioMoveExecutor`
- `FactorioClient`
- typed adapter response `MoveToCommandResult`

### 7. Runner improved for demo usefulness
`run_single_action(...)` now supports:
- explicit executor selection (`stub`, `factorio`)
- explicit `run_id`
- explicit `raw_state`
- explicit `candidate_action`

### 8. Action factory added
Implemented:
- `Action.move_to(...)`

This is now the preferred way to build default / demo movement actions.

### 9. Test coverage expanded
Added / expanded tests for:
- contract validation
- pass-through world-state validation behavior
- executor contracts
- action factory behavior
- pipeline behavior
- custom run IDs
- explicit raw state
- explicit candidate actions

## Verified behavior

The following behaviors were verified during the session through user-run tests and error-driven corrections:

- state contracts parse valid demo state and reject malformed state
- action validator enforces required fields for:
  - `MOVE_TO`
  - `PLACE_ENTITY`
  - `CRAFT_RECIPE`
  - `MINE_RESOURCE`
  - `INTERACT_ENTITY`
- `INTERACT_ENTITY` is validated by `target_entity_id`
- `MINE_RESOURCE` is validated by resource name plus target position
- `validate_world_state(...)` supports both raw mappings and `WorldState` inputs
- `StateNormalizationExpert` supports both raw mappings and `WorldState` inputs
- `ActionValidationExpert` supports both raw mappings and `WorldState` inputs
- `run_single_action(...)` supports:
  - `stub` executor
  - `factorio` executor
  - custom `run_id`
  - explicit `raw_state`
  - explicit `candidate_action`
- artifact files are written for the pipeline run
- debug artifacts and run audit propagate the correct `run_id`
- typed Factorio adapter seam and executor seam were brought back into alignment after mismatch regressions
- `Action.move_to(...)` builds the expected bounded action

## Files or modules touched

### Contracts
- `contracts/world_state.py`
- `contracts/actions.py`
- `contracts/artifacts.py`
- `contracts/expert_debug.py`

### Validation
- `validation/state_validator.py`
- `validation/action_validator.py`

### Experts
- `experts/state_normalization_expert.py`
- `experts/action_validation_expert.py`

### Executors
- `executors/stub_action_executor.py`
- `executors/factorio_move_executor.py`

### Integration
- `integrations/factorio/factorio_client.py`

### Runner / orchestration
- `director/run_single_action.py`

### Artifact writing
- `artifacts/run_artifact_writer.py`

### Fixtures
- `fixtures/mock_world_state.json`

### Tests
- `tests/test_contract_validation.py`
- `tests/test_run_single_action_pipeline.py`
- `tests/test_factorio_move_executor_contract.py`
- `tests/test_action_factories.py`
- `tests/test_expert_contracts.py`

## Important implementation details

### Architecture boundaries preserved
The system remains:
- deterministic
- non-agentic
- explicit in orchestration
- artifact-driven
- bounded by contracts

The Director has remained thin. It orchestrates. It does not reason.

### Current demo slice
The current slice is intentionally narrow and centered on:
- normalized state
- bounded `MOVE_TO`
- explicit executor choice
- artifact persistence

### Executor behavior
- `StubActionExecutor` is intentionally honest:
  - movement accepted
  - movement not marked completed
- `FactorioMoveExecutor` uses a typed adapter seam and maps adapter fields into the typed execution result

### Adapter seam
`FactorioClient` currently exposes:
- `get_player_position() -> Position`
- `move_to(x, y) -> MoveToCommandResult`

This is still a demo seam, not live Factorio ingestion.

### Artifact model
Current run artifacts:
- `input_state_snapshot.json`
- `state_normalization_debug.json`
- `validated_action.json`
- `action_validation_debug.json`
- `execution_result.json`
- `run_audit.json`

### Action factory
Default movement action construction should now prefer:
- `Action.move_to(...)`

instead of rebuilding the `params.target_position` shape inline.

## Current system state

The system is currently at a **credible architectural demo checkpoint**.

What exists now:
- typed contracts
- deterministic validation
- bounded experts
- explicit runner orchestration
- explicit executor selection
- typed execution results
- typed Factorio adapter seam
- persisted artifacts
- a growing test suite that covers the major control-plane seams

What does not yet exist:
- live Factorio world-state ingestion
- real world refresh after execution
- general action coverage beyond the current bounded demo path
- planning experts
- production or logistics reasoning
- UI / visualization layer
- replay viewer or artifact browser

## Known issues / remaining work

### Known issues
- No verified README file was created in-session. README text was drafted, but file creation was not confirmed.
- Git push timing was discussed and recommended, but actual push completion was not verified in-session.
- Several regressions in the session came from partial saves / stale file versions rather than design flaws. This is a process hazard worth remembering.

### Remaining work
- create / verify `README.md`
- verify repo status and push current checkpoint to git
- add a live state-ingestion seam if demo needs to show real game read path
- add post-execution observation / before-after state comparison
- add one more bounded action slice if needed for a richer demo
- eventually add a minimal visualization if the audience needs something beyond JSON artifacts

## Recommended next step

**Recommended next step: add a post-execution observation step to the runner and artifact set.**

Why this is the best next step:
- it improves demo value directly
- it does not require broad new capability
- it shows the architecture closing the loop from action request to observed world state
- it makes the “Factorio MES” feel more real than another round of contract polishing

A good bounded version would be:
1. execute `MOVE_TO`
2. ask adapter for current player position
3. persist a post-execution observation artifact
4. include the observation in the run audit or a separate artifact

That would move the demo from “we sent a command” to “we observed system state after command.”

## Safe stopping point

Safe stopping point reached.

The repo has:
- a coherent demo pipeline
- typed seams in the important places
- explicit orchestration
- passing behavior reported after the last round of fixes
- enough structure to share with others as a progress checkpoint

It is safe to stop here and resume from this artifact without needing to reconstruct the session from chat history.

## Resume instruction

Resume from the current deterministic demo pipeline checkpoint.

Do **not** redesign architecture.
Do **not** widen scope casually.
Preserve:
- deterministic behavior
- non-agentic design
- thin Director
- bounded experts
- typed contracts
- explicit executor selection
- artifact-first workflow

Start by verifying current test status and repo status, then move to the recommended next step: add a post-execution observation artifact through the existing Factorio adapter seam.

## Bottom line

This session turned the project from a promising folder structure into a real deterministic demo pipeline with typed contracts, explicit orchestration, explicit executor selection, artifact persistence, and enough test coverage to make the architecture credible. The most valuable next move is no longer more contract polishing; it is closing the demo loop by observing state after execution.

## Copy-paste continuation prompt for the next chat

Resume Factorio MES from the current deterministic demo pipeline checkpoint.

Authoritative state:
- typed contracts exist for world state, actions, debug artifacts, execution results, and run audit
- validators exist and are bounded
- `run_single_action(...)` supports explicit `executor_type`, `run_id`, `raw_state`, and `candidate_action`
- `Action.move_to(...)` exists and should be preferred for default/demo movement actions
- `StubActionExecutor` and `FactorioMoveExecutor` are both aligned to typed execution results
- `FactorioClient` currently exposes a typed movement seam, but no live state-ingestion loop
- current artifacts include input snapshot, expert debug artifacts, validated action, execution result, and run audit
- tests were reported green after the last correction cycle
- README text was drafted in chat but file creation was not verified
- git push was recommended but not verified

Required approach:
- preserve deterministic, non-agentic MES architecture
- keep Director thin
- do not redesign
- use bounded steps
- ask for files before patching if exact code is needed

Recommended next step:
add a post-execution observation step and artifact so the demo can show not just that a movement command was issued, but also what state was observed afterward.
