# Factorio Modular Expert System

A deterministic, non-agentic Modular Expert System for Factorio.

This project is a **demo architecture** intended to show how a bounded expert system can reason about Factorio state, validate legal actions, route execution explicitly, and persist artifacts for replay and inspection.

It is **not** a production tool.
It is **not** an autonomous agent framework.
It is **not** an LLM-driven controller.

The point is to make the architecture visible.

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

## Current Demo Slice

Today, the repo demonstrates a small but real control plane:

1. load a game-state snapshot
2. normalize and validate state
3. validate a bounded action
4. execute through an explicit executor path
5. persist artifacts for inspection

Current supported demo action:

- `MOVE_TO`

Current executor paths:

- `stub`
- `factorio`

The `stub` executor proves the architecture.
The `factorio` executor proves the adapter seam.

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
  - sample state used for demo runs
- `tests/`
  - contract and pipeline tests

---

## What Exists Right Now

### Contracts
The repo currently has typed contracts for:

- normalized world state
- legal actions
- expert debug artifacts
- execution results
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
Current Factorio adapter surface:

- `get_player_position()`
- `move_to(x, y)`

---

## What This Repo Is Trying To Show

This repo is trying to show that a game-playing system does **not** need to be an opaque “AI agent.”

You can build a clear architecture instead:

- observe state through explicit contracts
- validate actions before execution
- keep reasoning bounded
- route execution explicitly
- persist artifacts for replay
- keep each layer inspectable

For this project, that matters more than pretending to be human.

---

## Running Tests

From the repo root:

```bash
pytest -q