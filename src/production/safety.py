from __future__ import annotations

from typing import Dict, Optional


class SafetyGuard:
    def __init__(self, max_actions_per_tick: int = 250) -> None:
        self.max_actions_per_tick = max_actions_per_tick

    def validate(self, action: Optional[Dict[str, str]], agent_name: str) -> bool:
        if not action:
            return False
        if action.get("action", "wait") == "wait":
            return False
        if not agent_name:
            return False
        return True
