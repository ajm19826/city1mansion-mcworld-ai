from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.engine.citizen import Citizen
from src.engine.world import City, World


@dataclass
class CityPlan:
    plan_id: str
    description: str
    approved: bool = False
    priority: int = 1


@dataclass
class Permit:
    permit_id: str
    requester_id: str
    description: str
    approved: bool = False


@dataclass
class GovernmentSystem:
    world: World
    laws: List[str] = field(default_factory=lambda: [
        "tax compliance",
        "building safety",
        "public transport maintenance",
        "resource extraction licensing",
    ])
    city_plans: Dict[str, List[CityPlan]] = field(default_factory=dict)
    permits: Dict[str, Permit] = field(default_factory=dict)

    def bootstrap_government(self, citizens: List[Citizen]) -> None:
        for city_name, city in self.world.cities.items():
            residents = [citizen for citizen in citizens if citizen.city == city_name and not citizen.is_child]
            if not residents:
                continue
            mayor = random.choice(residents)
            governor = random.choice(residents)
            self.world.governments[city_name].mayor = mayor.citizen_id
            self.world.governments[city_name].governor = governor.citizen_id
            self.world.governments[city_name].police_force = [resident.citizen_id for resident in residents[: max(1, len(residents) // 100)]]
            mayor.add_memory(f"Elected mayor of {city_name}.", importance=3)
            governor.add_memory(f"Assigned governor duties for {city_name}.", importance=3)

    def request_build_permit(self, citizen: Citizen, description: str) -> Permit:
        permit = Permit(
            permit_id=f"permit_{len(self.permits) + 1:04d}",
            requester_id=citizen.citizen_id,
            description=description,
        )
        permit.approved = random.random() > 0.2
        self.permits[permit.permit_id] = permit
        citizen.add_memory(f"Submitted permit request: {description}.", importance=2)
        if permit.approved:
            citizen.add_memory("Permit approved.", importance=2)
        else:
            citizen.add_memory("Permit denied.", importance=2)
        return permit

    def review_city_plan(self, city: City, description: str) -> CityPlan:
        plan = CityPlan(plan_id=f"plan_{len(self.city_plans.get(city.name, [])) + 1:04d}", description=description)
        plan.approved = random.random() > 0.3
        self.city_plans.setdefault(city.name, []).append(plan)
        return plan

    def assess_law_compliance(self, citizen: Citizen) -> bool:
        if citizen.job.title == "Illegal Builder" or citizen.balance < 0:
            return False
        return True

    def enforce_policy(self, city_name: str) -> None:
        government = self.world.governments.get(city_name)
        if not government:
            return
        if random.random() < 0.05:
            government.tax_rate = min(0.25, government.tax_rate + 0.01)
        else:
            government.tax_rate = max(0.05, government.tax_rate - 0.005)
