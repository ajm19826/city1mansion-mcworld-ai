from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List

from src.engine.citizen import Citizen
from src.engine.world import Mine, World


@dataclass
class MiningCompany:
    company_id: str
    name: str
    owner_id: str
    employees: List[str] = field(default_factory=list)
    output_capacity: float = 1.0

    def operate(self, world: World) -> Dict[str, float]:
        extracted: Dict[str, float] = {}
        worker_count = max(1, len(self.employees))
        for city in world.cities.values():
            for mine in city.mines:
                if mine.discovered:
                    amount = mine.yield_rate * worker_count * random.uniform(0.8, 1.2)
                    extracted[mine.resource_type] = extracted.get(mine.resource_type, 0.0) + amount
        return extracted


@dataclass
class MiningSystem:
    companies: Dict[str, MiningCompany] = field(default_factory=dict)
    known_resources: Dict[str, float] = field(default_factory=lambda: {
        "coal": 0.0,
        "iron": 0.0,
        "gold": 0.0,
        "diamonds": 0.0,
        "stone": 0.0,
        "rare": 0.0,
    })

    def discover_mine(self, world: World, city_name: str, resource_type: str) -> None:
        city = world.get_city(city_name)
        if not city:
            return
        location = city.buildings[0].location if city.buildings else None
        if location is None:
            from src.engine.world import Location
            location = Location(
                address=f"{city_name} Mining Zone",
                city=city.name,
                territory=city.territory,
                country=city.country,
            )

        existing_ids = {mine.mine_id for mine in city.mines}
        suffix = 0
        mine_id = f"mine_{city.name}_{resource_type}_{suffix}"
        while mine_id in existing_ids:
            suffix += 1
            mine_id = f"mine_{city.name}_{resource_type}_{suffix}"

        mine = Mine(
            mine_id=mine_id,
            name=f"{city_name} {resource_type.title()} Mine",
            location=location,
            resource_type=resource_type,
            yield_rate=random.uniform(0.5, 3.0),
            discovered=True,
        )
        city.mines.append(mine)

    def mine_resources(self, world: World) -> None:
        for company in self.companies.values():
            extracted = company.operate(world)
            for resource, amount in extracted.items():
                world.resources[resource] = world.resources.get(resource, 0.0) + amount
                self.known_resources[resource] = self.known_resources.get(resource, 0.0) + amount

    def register_company(self, company: MiningCompany) -> None:
        self.companies[company.company_id] = company

    def assign_workers(self, company_id: str, worker_ids: List[str]) -> None:
        company = self.companies.get(company_id)
        if company:
            company.employees.extend(worker_ids)
