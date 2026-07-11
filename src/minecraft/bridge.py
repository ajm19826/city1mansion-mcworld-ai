from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class MinecraftBridge:
    def __init__(self, world_path: Optional[str] = None) -> None:
        self.world_path = Path(world_path or "./minecraft_world")
        self.state_path = self.world_path / "minecraftia" / "bridge_state.json"
        self.commands_path = self.world_path / "minecraftia" / "commands.jsonl"
        self.mcfunction_path = self.world_path / "minecraftia" / "minecraftia_bridge.mcfunction"
        self.state: Dict[str, Any] = {"tick": 0, "actions": []}
        self._load_state()

    def _load_state(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        if self.state_path.exists():
            with self.state_path.open("r", encoding="utf-8") as handle:
                self.state = json.load(handle)

    def _save_state(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with self.state_path.open("w", encoding="utf-8") as handle:
            json.dump(self.state, handle, indent=2, sort_keys=True)

    def record_command(self, command: Dict[str, Any]) -> None:
        self.commands_path.parent.mkdir(parents=True, exist_ok=True)
        with self.commands_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(command) + "\n")
        self.state.setdefault("actions", []).append(command)
        self.state["tick"] = int(self.state.get("tick", 0)) + 1
        self._write_mcfunction(command)
        self._save_state()

    def emit_build_command(self, agent: str, location: str, block_type: str = "oak_planks") -> None:
        self.record_command({"type": "build", "agent": agent, "location": location, "block": block_type})

    def emit_explore_command(self, agent: str, location: str) -> None:
        self.record_command({"type": "explore", "agent": agent, "location": location})

    def emit_govern_command(self, agent: str, action: str) -> None:
        self.record_command({"type": "govern", "agent": agent, "action": action})

    def emit_economy_command(self, agent: str, action: str) -> None:
        self.record_command({"type": "economy", "agent": agent, "action": action})

    def _write_mcfunction(self, command: Dict[str, Any]) -> None:
        self.mcfunction_path.parent.mkdir(parents=True, exist_ok=True)
        with self.mcfunction_path.open("a", encoding="utf-8") as handle:
            cmd_type = command.get("type", "noop")
            if cmd_type == "build":
                handle.write(f"# build {command.get('agent', 'unknown')} at {command.get('location', 'unknown')}\n")
            elif cmd_type == "explore":
                handle.write(f"# explore {command.get('agent', 'unknown')} at {command.get('location', 'unknown')}\n")
            elif cmd_type == "govern":
                handle.write(f"# govern {command.get('agent', 'unknown')} -> {command.get('action', 'unknown')}\n")
            elif cmd_type == "economy":
                handle.write(f"# economy {command.get('agent', 'unknown')} -> {command.get('action', 'unknown')}\n")
            else:
                handle.write(f"# {cmd_type}\n")

    def load_commands(self) -> List[Dict[str, Any]]:
        if not self.commands_path.exists():
            return []
        with self.commands_path.open("r", encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]
