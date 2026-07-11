from __future__ import annotations

from typing import Dict

from src.ai.agent import CitizenAgent, AgentState


class EconomyAgent(CitizenAgent):
    def __init__(self, state: AgentState) -> None:
        super().__init__(state)
        self.state.role = "Economy Manager"

    def think(self, context: Dict[str, object]) -> Dict[str, str]:
        balance = float(context.get("balance", 0.0))
        if balance > 50000:
            decision = {
                "decision": "expand_business",
                "rationale": "Strong finances support business expansion.",
                "action": "invest",
                "priority": "high",
            }
        else:
            decision = {
                "decision": "stabilize_trade",
                "rationale": "Protect cash flow and maintain trade stability.",
                "action": "adjust_prices",
                "priority": "medium",
            }
        self.last_decision = decision
        self.memory.add(f"Economy decision: {decision['decision']}", importance=4, memory_type="long_term")
        return decision
