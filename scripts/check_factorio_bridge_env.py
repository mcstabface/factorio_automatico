from __future__ import annotations

import json
import os
import socket
import sys
from pathlib import Path


def _env_value(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def _command_script_path(command_value: str | None, repo_root: Path) -> str | None:
    if not command_value:
        return None

    parts = command_value.split()
    if len(parts) < 2:
        return None

    if parts[0] != "python":
        return None

    script_path = repo_root / parts[1]
    return str(script_path)


def _port_listening(host: str, port: int, timeout_seconds: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True
    except OSError:
        return False


def _status(
    *,
    ok: bool,
    details: str,
    value: object | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "ok": ok,
        "details": details,
    }
    if value is not None:
        payload["value"] = value
    return payload


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent

    rcon_host = _env_value("FACTORIO_RCON_HOST")
    rcon_port_raw = _env_value("FACTORIO_RCON_PORT")
    rcon_password = _env_value("FACTORIO_RCON_PASSWORD")
    user_data_dir_raw = _env_value("FACTORIO_USER_DATA_DIR")
    position_command = _env_value("FACTORIO_POSITION_COMMAND")
    raw_position_command = _env_value("FACTORIO_RAW_POSITION_COMMAND")
    move_to_command = _env_value("FACTORIO_MOVE_TO_COMMAND")
    walk_step_seconds = _env_value("FACTORIO_WALK_STEP_SECONDS")

    results: dict[str, dict[str, object]] = {}

    results["FACTORIO_RCON_HOST"] = _status(
        ok=rcon_host is not None,
        details="set" if rcon_host else "missing",
        value=rcon_host,
    )

    rcon_port: int | None = None
    if rcon_port_raw is None:
        results["FACTORIO_RCON_PORT"] = _status(
            ok=False,
            details="missing",
        )
    else:
        try:
            rcon_port = int(rcon_port_raw)
            results["FACTORIO_RCON_PORT"] = _status(
                ok=True,
                details="set",
                value=rcon_port,
            )
        except ValueError:
            results["FACTORIO_RCON_PORT"] = _status(
                ok=False,
                details="not an integer",
                value=rcon_port_raw,
            )

    results["FACTORIO_RCON_PASSWORD"] = _status(
        ok=rcon_password is not None,
        details="set" if rcon_password else "missing",
        value="***set***" if rcon_password else None,
    )

    user_data_dir: Path | None = None
    if user_data_dir_raw is None:
        results["FACTORIO_USER_DATA_DIR"] = _status(
            ok=False,
            details="missing",
        )
    else:
        user_data_dir = Path(user_data_dir_raw)
        results["FACTORIO_USER_DATA_DIR"] = _status(
            ok=user_data_dir.exists(),
            details="exists" if user_data_dir.exists() else "path does not exist",
            value=str(user_data_dir),
        )

    for env_name, env_value in (
        ("FACTORIO_POSITION_COMMAND", position_command),
        ("FACTORIO_RAW_POSITION_COMMAND", raw_position_command),
        ("FACTORIO_MOVE_TO_COMMAND", move_to_command),
    ):
        script_path_raw = _command_script_path(env_value, repo_root)
        if env_value is None:
            results[env_name] = _status(
                ok=False,
                details="missing",
            )
            continue

        if script_path_raw is None:
            results[env_name] = _status(
                ok=False,
                details="expected format like: python scripts/....py",
                value=env_value,
            )
            continue

        script_path = Path(script_path_raw)
        results[env_name] = _status(
            ok=script_path.exists(),
            details="script exists" if script_path.exists() else "script path does not exist",
            value=env_value,
        )

    if walk_step_seconds is None:
        results["FACTORIO_WALK_STEP_SECONDS"] = _status(
            ok=False,
            details="missing",
        )
    else:
        try:
            results["FACTORIO_WALK_STEP_SECONDS"] = _status(
                ok=float(walk_step_seconds) > 0.0,
                details="set" if float(walk_step_seconds) > 0.0 else "must be > 0",
                value=walk_step_seconds,
            )
        except ValueError:
            results["FACTORIO_WALK_STEP_SECONDS"] = _status(
                ok=False,
                details="not numeric",
                value=walk_step_seconds,
            )

    if user_data_dir is None:
        results["script_output_dir"] = _status(
            ok=False,
            details="cannot evaluate because FACTORIO_USER_DATA_DIR is missing",
        )
        results["server_mod_dir"] = _status(
            ok=False,
            details="cannot evaluate because FACTORIO_USER_DATA_DIR is missing",
        )
        results["server_mod_files"] = _status(
            ok=False,
            details="cannot evaluate because FACTORIO_USER_DATA_DIR is missing",
        )
    else:
        script_output_dir = user_data_dir / "script-output" / "chatgpt"
        server_mod_dir = user_data_dir / "mods" / "chatgpt_bridge_0.1.0"
        info_json = server_mod_dir / "info.json"
        control_lua = server_mod_dir / "control.lua"

        results["script_output_dir"] = _status(
            ok=script_output_dir.exists(),
            details="exists" if script_output_dir.exists() else "directory does not exist yet",
            value=str(script_output_dir),
        )
        results["server_mod_dir"] = _status(
            ok=server_mod_dir.exists(),
            details="exists" if server_mod_dir.exists() else "directory does not exist",
            value=str(server_mod_dir),
        )
        results["server_mod_files"] = _status(
            ok=info_json.exists() and control_lua.exists(),
            details=(
                "info.json and control.lua present"
                if info_json.exists() and control_lua.exists()
                else "missing info.json and/or control.lua"
            ),
            value={
                "info_json": str(info_json),
                "control_lua": str(control_lua),
            },
        )

    if rcon_host is None or rcon_port is None:
        results["rcon_listener"] = _status(
            ok=False,
            details="cannot evaluate because host/port is missing or invalid",
        )
    else:
        listening = _port_listening(rcon_host, rcon_port)
        results["rcon_listener"] = _status(
            ok=listening,
            details="accepting connections" if listening else "not accepting connections",
            value=f"{rcon_host}:{rcon_port}",
        )

    overall_ok = all(item["ok"] for item in results.values())

    summary = {
        "overall_ok": overall_ok,
        "repo_root": str(repo_root),
        "checks": results,
    }

    print(json.dumps(summary, indent=2))

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())