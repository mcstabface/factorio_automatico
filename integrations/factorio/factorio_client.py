from __future__ import annotations


class FactorioClient:
    def get_player_position(self) -> dict[str, float]:
        return {"x": 0.0, "y": 0.0}

    def move_to(self, x: float, y: float) -> dict[str, object]:
        return {
            "started": True,
            "completed": False,
            "command": "move_to",
            "target_position": {
                "x": float(x),
                "y": float(y),
            },
        }