from __future__ import annotations

from typing import Dict

from src.ai.agent import CitizenAgent, AgentState


class ConstructionAgent(CitizenAgent):
    def __init__(self, state: AgentState) -> None:
        super().__init__(state)
        self.state.role = "Construction Agent"

    def think(self, context: Dict[str, object]) -> Dict[str, str]:
        if context.get("damaged"):
            decision = {
                "decision": "repair_structure",
                "rationale": "A damaged structure needs repair.",
                "action": "assign_workers",
                "priority": "high",
            }
        else:
            decision = {
                "decision": "plan_construction",
                "rationale": "Propose a new construction project.",
                "action": "create_project",
                "priority": "medium",
            }
        self.last_decision = decision
        self.memory.add(f"Construction decision: {decision['decision']}", importance=3, memory_type="long_term")
        return decision
