from __future__ import annotations

from typing import List, Optional

from src.engine.citizen import Citizen


class AIManager:
    def __init__(self) -> None:
        self.adult_model_name = "adult_model_750m"
        self.child_model_name = "child_model_300m"
        self.active_queue: List[str] = []

    def select_active_citizens(self, citizens: List[Citizen], player_location: Optional[str] = None) -> List[Citizen]:
        active = [citizen for citizen in citizens if citizen.active]
        if len(active) >= 250:
            return active[:250]

        if player_location:
            nearby = [citizen for citizen in citizens if citizen.city == player_location]
            active.extend(nearby[: max(0, 250 - len(active))])

        if len(active) < 250:
            active.extend(citizens[: max(0, 250 - len(active))])

        return active

    def run_decision_cycle(self, citizen: Citizen) -> None:
        if citizen.is_child:
            self._child_decision(citizen)
        else:
            self._adult_decision(citizen)

    def _adult_decision(self, citizen: Citizen) -> None:
        if citizen.job.title == "Construction Worker" and citizen.skills.building > 70:
            citizen.add_memory("Completed construction planning task.", importance=3)
        elif citizen.job.title == "Teacher":
            citizen.add_memory("Reviewed student progress.", importance=2)
        elif citizen.job.title == "Business Owner":
            citizen.add_memory("Checked market trends.", importance=2)
        else:
            citizen.add_memory("Considered daily responsibilities.", importance=1)

    def _child_decision(self, citizen: Citizen) -> None:
        citizen.add_memory("Attended school lessons.", importance=1)
        citizen.skills.building = min(citizen.skills.building + 1, 100)
        citizen.skills.mining = min(citizen.skills.mining + 1, 100)

    def estimate_model_memory(self) -> int:
        return 1024 if self.adult_model_name else 512
