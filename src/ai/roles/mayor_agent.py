from __future__ import annotations

from typing import Dict, List

from src.ai.agent import CitizenAgent, AgentState


class MayorAgent(CitizenAgent):
    def __init__(self, state: AgentState) -> None:
        super().__init__(state)
        self.state.role = "Mayor"

    def think(self, context: Dict[str, object]) -> Dict[str, str]:
        issue = context.get("issue", "public services")
        if "road" in str(issue).lower() or "infrastructure" in str(issue).lower():
            decision = {
                "decision": "approve_infrastructure",
                "rationale": "Infrastructure keeps the city functioning.",
                "action": "fund_repairs",
                "priority": "high",
            }
        else:
            decision = {
                "decision": "stabilize_services",
                "rationale": "Maintain public order and services.",
                "action": "review_budget",
                "priority": "medium",
            }
        self.last_decision = decision
        self.memory.add(f"Mayor decision: {decision['decision']}", importance=4, memory_type="long_term")
        return decision
