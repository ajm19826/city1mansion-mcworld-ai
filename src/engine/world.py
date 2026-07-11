from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Location:
    address: str
    city: str
    territory: str
    country: str


@dataclass
class Building:
    building_id: str
    name: str
    location: Location
    structure_type: str
    condition: int = 100
    owner: Optional[str] = None
    damaged: bool = False


@dataclass
class Road:
    road_id: str
    name: str
    start: Location
    end: Location
    condition: int = 100
    capacity: int = 100


@dataclass
class Mine:
    mine_id: str
    name: str
    location: Location
    resource_type: str
    yield_rate: float
    discovered: bool = False


@dataclass
class City:
    name: str
    territory: str
    country: str
    population: int = 0
    buildings: List[Building] = field(default_factory=list)
    roads: List[Road] = field(default_factory=list)
    mines: List[Mine] = field(default_factory=list)


@dataclass
class Government:
    mayor: Optional[str] = None
    governor: Optional[str] = None
    judges: List[str] = field(default_factory=list)
    police_force: List[str] = field(default_factory=list)
    tax_rate: float = 0.12


@dataclass
class World:
    name: str
    territory: str
    country: str
    cities: Dict[str, City] = field(default_factory=dict)
    governments: Dict[str, Government] = field(default_factory=dict)
    resources: Dict[str, float] = field(default_factory=lambda: {
        "coal": 0.0,
        "iron": 0.0,
        "gold": 0.0,
        "diamonds": 0.0,
        "stone": 0.0,
        "rare": 0.0,
    })

    def register_city(self, city: City) -> None:
        self.cities[city.name] = city
        self.governments[city.name] = Government()

    def get_city(self, name: str) -> Optional[City]:
        return self.cities.get(name)

    def get_government(self, city_name: str) -> Optional[Government]:
        return self.governments.get(city_name)

    def add_building(self, city_name: str, building: Building) -> None:
        city = self.get_city(city_name)
        if city:
            city.buildings.append(building)

    def add_road(self, city_name: str, road: Road) -> None:
        city = self.get_city(city_name)
        if city:
            city.roads.append(road)
