from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List


class ProductionStateStore:
    def __init__(self, path: str = "state/production_state.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {"events": [], "world_actions": []}
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def save(self, data: Dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)

    def append_event(self, event: Dict[str, Any]) -> None:
        data = self.load()
        data.setdefault("events", []).append(event)
        if len(data["events"]) > 10000:
            data["events"] = data["events"][-10000:]
        self.save(data)

    def append_action(self, action: Dict[str, Any]) -> None:
        data = self.load()
        data.setdefault("world_actions", []).append(action)
        if len(data["world_actions"]) > 10000:
            data["world_actions"] = data["world_actions"][-10000:]
        self.save(data)
