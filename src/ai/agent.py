from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.ai.memory import MemorySystem


@dataclass
class AgentState:
    name: str
    role: str
    city: str
    job: str
    personality: str = "practical"
    goals: List[str] = field(default_factory=list)
    skills: Dict[str, int] = field(default_factory=dict)
    relationships: Dict[str, str] = field(default_factory=dict)
    financial_status: float = 0.0
    location: str = "home"
    history: List[str] = field(default_factory=list)


class CitizenAgent:
    def __init__(self, state: AgentState) -> None:
        self.state = state
        self.memory = MemorySystem()
        self.last_decision: Optional[Dict[str, str]] = None

    def think(self, context: Dict[str, object]) -> Dict[str, str]:
        decision = {
            "decision": "observe",
            "rationale": "No urgent decision required.",
            "action": "wait",
            "priority": "low",
        }
        self.last_decision = decision
        self.memory.add(f"Thought about: {context}", importance=2)
        return decision

    def communicate(self, message: str) -> None:
        self.memory.add(f"Spoke: {message}", importance=2)

    def remember(self, event: str, importance: int = 2, long_term: bool = False) -> None:
        self.memory.add(event, importance=importance, memory_type="long_term" if long_term else "short_term")

    def plan(self, goal: str) -> None:
        self.state.goals.append(goal)
        self.memory.add(f"Planned goal: {goal}", importance=3)
