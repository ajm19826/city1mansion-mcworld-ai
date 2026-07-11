from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.engine.citizen import Citizen
from src.engine.world import Mine, World


@dataclass
class Discovery:
    discovery_id: str
    discoverer_id: str
    location: str
    discovery_type: str
    description: str
    timestamp: str


@dataclass
class ExplorationSystem:
    discoveries: List[Discovery] = field(default_factory=list)
    explored_areas: Dict[str, bool] = field(default_factory=dict)

    def explore_area(self, explorer: Citizen, world: World) -> Optional[Discovery]:
        from datetime import datetime

        if random.random() < 0.3:
            discovery_type = random.choice(["mine", "fertile_land", "water_source", "resource_deposit"])
            city = world.get_city(explorer.city)
            if not city:
                return None

            if discovery_type == "mine" and random.random() > 0.7:
                resource = random.choice(["coal", "iron", "gold", "diamonds", "stone", "rare"])
                discovery = Discovery(
                    discovery_id=f"discovery_{len(self.discoveries)}",
                    discoverer_id=explorer.citizen_id,
                    location=explorer.city,
                    discovery_type="mine",
                    description=f"Found {resource.title()} deposit north of {explorer.city}",
                    timestamp=datetime.utcnow().isoformat(),
                )
                self.discoveries.append(discovery)
                explorer.add_memory(f"Discovered {resource} mine. Skill +1", importance=3)
                explorer.skills.mining = min(100, explorer.skills.mining + 1)
                return discovery

            elif discovery_type == "fertile_land":
                discovery = Discovery(
                    discovery_id=f"discovery_{len(self.discoveries)}",
                    discoverer_id=explorer.citizen_id,
                    location=explorer.city,
                    discovery_type="fertile_land",
                    description=f"Found suitable farmland location in {explorer.city}",
                    timestamp=datetime.utcnow().isoformat(),
                )
                self.discoveries.append(discovery)
                explorer.add_memory("Located fertile land for farming.", importance=2)
                return discovery

            elif discovery_type == "water_source":
                discovery = Discovery(
                    discovery_id=f"discovery_{len(self.discoveries)}",
                    discoverer_id=explorer.citizen_id,
                    location=explorer.city,
                    discovery_type="water_source",
                    description=f"Found fresh water source near {explorer.city}",
                    timestamp=datetime.utcnow().isoformat(),
                )
                self.discoveries.append(discovery)
                explorer.add_memory("Located water source.", importance=2)
                return discovery

        return None

    def process_explorations(self, citizens: List[Citizen], world: World) -> None:
        explorers = random.sample(citizens, k=min(20, len(citizens) // 100))
        for explorer in explorers:
            if explorer.skills.driving > 30 and random.random() < 0.2:
                self.explore_area(explorer, world)

    def get_discovery_report(self) -> str:
        total = len(self.discoveries)
        mine_count = sum(1 for d in self.discoveries if d.discovery_type == "mine")
        resource_count = sum(1 for d in self.discoveries if d.discovery_type == "resource_deposit")
        location_count = sum(1 for d in self.discoveries if d.discovery_type in ["fertile_land", "water_source"])
        return f"Discoveries: {total} (Mines: {mine_count}, Resources: {resource_count}, Locations: {location_count})"
