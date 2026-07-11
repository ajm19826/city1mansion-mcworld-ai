from __future__ import annotations

from typing import Dict, Any


class PromptBuilder:
    @staticmethod
    def build_decision_prompt(agent_name: str, role: str, context: Dict[str, Any]) -> str:
        return (
            f"You are {agent_name}, a {role}.\n"
            f"Context: {context}\n"
            "Respond with a concise JSON object containing: "
            "decision, rationale, action, priority."
        )
