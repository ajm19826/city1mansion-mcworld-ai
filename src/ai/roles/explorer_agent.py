from __future__ import annotations

from typing import Dict

from src.ai.agent import CitizenAgent, AgentState


class ExplorerAgent(CitizenAgent):
    def __init__(self, state: AgentState) -> None:
        super().__init__(state)
        self.state.role = "Explorer"

    def think(self, context: Dict[str, object]) -> Dict[str, str]:
        decision = {
            "decision": "explore_area",
            "rationale": "Explore nearby territory for resources and routes.",
            "action": "survey_region",
            "priority": "medium",
        }
        self.last_decision = decision
        self.memory.add(f"Exploration decision: {decision['decision']}", importance=3, memory_type="long_term")
        return decision
