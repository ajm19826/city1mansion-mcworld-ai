from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.engine.world import Building, Location


@dataclass
class WorldAction:
    action_type: str
    target: str
    payload: Dict[str, object] = field(default_factory=dict)


class WorldActionExecutor:
    def __init__(self) -> None:
        self.actions: List[WorldAction] = []

    def execute(self, action: Optional[Dict[str, str]], agent_name: str, world: Optional[object] = None) -> Optional[WorldAction]:
        if not action:
            return None
        action_type = action.get("action", "wait")
        if action_type == "assign_workers":
            world_action = WorldAction("construction", agent_name, {"task": "repair_structure"})
        elif action_type == "create_project":
            world_action = WorldAction("construction", agent_name, {"task": "new_project"})
        elif action_type == "survey_region":
            world_action = WorldAction("exploration", agent_name, {"task": "survey_region"})
        elif action_type == "fund_repairs":
            world_action = WorldAction("government", agent_name, {"task": "fund_repairs"})
        elif action_type == "adjust_prices":
            world_action = WorldAction("economy", agent_name, {"task": "adjust_prices"})
        else:
            world_action = WorldAction("idle", agent_name, {"task": "wait"})

        if world and world_action.action_type == "construction":
            city_name = action.get("city") or next(iter(world.cities), None)
            if city_name and city_name in world.cities:
                city = world.cities[city_name]
                building = Building(
                    building_id=f"autobuild_{len(city.buildings) + 1}",
                    name=f"{agent_name} Project",
                    location=Location(address=f"{len(city.buildings) + 1} {city_name}", city=city_name, territory=city.territory, country=city.country),
                    structure_type="AutoBuilt",
                    condition=90,
                    owner=agent_name,
                )
                city.buildings.append(building)
        elif world and world_action.action_type == "exploration":
            city_name = action.get("city") or next(iter(world.cities), None)
            if city_name and city_name in world.cities:
                world.resources["stone"] = world.resources.get("stone", 0.0) + 1.0
        elif world and world_action.action_type == "government":
            city_name = action.get("city") or next(iter(world.cities), None)
            if city_name and city_name in world.cities:
                city = world.cities[city_name]
                city.population = max(0, city.population + 1)
        elif world and world_action.action_type == "economy":
            world.resources["gold"] = world.resources.get("gold", 0.0) + 1.0

        self.actions.append(world_action)
        return world_action
