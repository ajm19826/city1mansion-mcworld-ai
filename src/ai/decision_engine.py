from __future__ import annotations

from typing import Dict, Optional

from src.ai.agent import CitizenAgent
from src.ai.prompts import PromptBuilder


class DecisionEngine:
    def __init__(self, model_enabled: bool = False) -> None:
        self.model_enabled = model_enabled
        self.last_prompt: Optional[str] = None

    def decide(self, agent: CitizenAgent, context: Dict[str, object]) -> Dict[str, str]:
        self.last_prompt = PromptBuilder.build_decision_prompt(
            agent.state.name,
            agent.state.role,
            context,
        )
        if self.model_enabled:
            return {
                "decision": "model_call",
                "rationale": "External model requested.",
                "action": "consult_model",
                "priority": "medium",
            }
        return agent.think(context)
