from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class MinecraftAction:
    action_type: str
    target: str
    details: Dict[str, object] = field(default_factory=dict)


class MinecraftIntegration:
    def __init__(self, enabled: bool = False, mode: str = "private_world", world_path: Optional[str] = None) -> None:
        self.enabled = enabled
        self.mode = mode
        self.world_path = Path(world_path or "./minecraft_world")
        self.actions: List[MinecraftAction] = []
        self.connected = False

    @property
    def world_path_obj(self) -> Path:
        return self.world_path if isinstance(self.world_path, Path) else Path(str(self.world_path))

    def connect(self) -> bool:
        if not self.enabled:
            self.connected = False
            return False
        self.world_path = self.world_path_obj
        self.world_path.mkdir(parents=True, exist_ok=True)
        (self.world_path / "minecraftia").mkdir(parents=True, exist_ok=True)
        self.connected = True
        return True

    def disconnect(self) -> None:
        self.connected = False

    def publish_action(self, action: MinecraftAction) -> None:
        if not self.connected:
            return
        self.actions.append(action)
        self.world_path = self.world_path_obj
        manifest_path = self.world_path / "minecraftia" / "actions.jsonl"
        with manifest_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({
                "action_type": action.action_type,
                "target": action.target,
                "details": action.details,
            }) + "\n")

    def execute_decision(self, decision: Dict[str, str], agent_name: str) -> Optional[MinecraftAction]:
        action_type = decision.get("action", "wait")
        if action_type == "assign_workers":
            return MinecraftAction("build", agent_name, {"task": "repair_structure"})
        if action_type == "create_project":
            return MinecraftAction("build", agent_name, {"task": "new_project"})
        if action_type == "survey_region":
            return MinecraftAction("explore", agent_name, {"task": "survey_region"})
        if action_type == "fund_repairs":
            return MinecraftAction("government", agent_name, {"task": "fund_repairs"})
        if action_type == "adjust_prices":
            return MinecraftAction("economy", agent_name, {"task": "adjust_prices"})
        return None
