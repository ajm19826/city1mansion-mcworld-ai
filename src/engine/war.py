from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List

from src.engine.world import World


@dataclass
class Army:
    army_id: str
    commander: str
    strength: int
    stationed_at: str


@dataclass
class Conflict:
    conflict_id: str
    aggressor: str
    defender: str
    reason: str
    intensity: int
    active: bool = True


@dataclass
class DiplomacySystem:
    world: World
    alliances: Dict[str, List[str]] = field(default_factory=dict)
    conflicts: List[Conflict] = field(default_factory=list)

    def declare_conflict(self, aggressor: str, defender: str, reason: str) -> Conflict:
        conflict = Conflict(
            conflict_id=f"conflict_{len(self.conflicts) + 1:04d}",
            aggressor=aggressor,
            defender=defender,
            reason=reason,
            intensity=random.randint(1, 5),
        )
        self.conflicts.append(conflict)
        return conflict

    def resolve_conflicts(self) -> None:
        for conflict in self.conflicts:
            if not conflict.active:
                continue
            if random.random() < 0.2:
                conflict.active = False
                if random.random() > 0.5:
                    self._adjust_territory(conflict)

    def _adjust_territory(self, conflict: Conflict) -> None:
        city = self.world.get_city(conflict.defender)
        if city and random.random() > 0.5:
            city.territory = conflict.aggressor

    def balance_power(self) -> None:
        for city_name in self.world.cities:
            if random.random() < 0.1:
                self.alliances.setdefault(city_name, []).append(random.choice(list(self.world.cities.keys())))
