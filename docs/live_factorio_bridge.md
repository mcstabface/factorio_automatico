## Launch flow

### Start the headless/server instance

Use the repo helper:

```bash
bash scripts/start_factorio_headless.sh
```

### Load the bridge environment

```bash
source scripts/set_factorio_bridge_env.sh
```

### Validate bridge readiness

```bash
python scripts/check_factorio_bridge_env.py
python scripts/demo_status.py
```

`demo_status.py` is the quickest wrapper-layer “what do I do next?” helper.

- if the live bridge is not ready, it recommends startup/validation commands
- if the live bridge is ready, it recommends the best demo/stream commands

### Run the current demo paths

```bash
python scripts/smoke_live_bridge.py
python scripts/run_live_factorio_demo.py
python scripts/run_live_factorio_stream_demo.py
python scripts/run_live_factorio_walk_to_target.py --trace 10 10
```

Recommended usage by purpose:

- machine-readable demo output:
  - `python scripts/run_live_factorio_demo.py`
- stream/screen-share friendly output:
  - `python scripts/run_live_factorio_stream_demo.py`
- direct step-by-step movement trace:
  - `python scripts/run_live_factorio_walk_to_target.py --trace 10 10`