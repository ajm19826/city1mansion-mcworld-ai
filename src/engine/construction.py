from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.engine.citizen import Citizen
from src.engine.world import Building, City, Location, World


@dataclass
class ConstructionProject:
    project_id: str
    name: str
    location: Location
    building_type: str
    progress: float = 0.0
    required_skill: int = 50
    workers: List[str] = field(default_factory=list)
    total_cost: float = 100000.0
    budget_spent: float = 0.0
    completion_date: Optional[str] = None
    active: bool = True

    def calculate_completion_rate(self) -> float:
        if not self.workers:
            return 0.0
        worker_count = len(self.workers)
        return min(1.0, worker_count * 0.15)

    def advance(self) -> None:
        if self.active:
            rate = self.calculate_completion_rate()
            self.progress = min(100.0, self.progress + rate)
            self.budget_spent += len(self.workers) * 500.0
            if self.progress >= 100.0:
                self.active = False


@dataclass
class ConstructionSystem:
    world: World
    projects: List[ConstructionProject] = field(default_factory=list)
    completed_buildings: List[Building] = field(default_factory=list)

    def create_project(self, name: str, location: Location, building_type: str, required_skill: int = 50) -> ConstructionProject:
        project = ConstructionProject(
            project_id=f"project_{id(self)}_{len(self.projects)}",
            name=name,
            location=location,
            building_type=building_type,
            required_skill=required_skill,
        )
        self.projects.append(project)
        return project

    def discover_damaged_structure(self, world: World) -> Optional[Building]:
        for city in world.cities.values():
            for building in city.buildings:
                if building.condition < 50 and not building.damaged:
                    building.damaged = True
                    return building
        return None

    def assign_workers(self, project_id: str, worker_ids: List[str], citizens: Dict[str, Citizen]) -> None:
        project = next((p for p in self.projects if p.project_id == project_id), None)
        if not project:
            return
        for worker_id in worker_ids:
            if worker_id not in project.workers:
                project.workers.append(worker_id)
                citizen = citizens.get(worker_id)
                if citizen:
                    citizen.add_memory(f"Assigned to construction project: {project.name}.", importance=2)

    def run_projects(self, citizens: Dict[str, Citizen]) -> None:
        for project in self.projects:
            project.advance()
            if project.progress >= 100.0 and project.active is False:
                self._finalize_project(project, citizens)

    def _finalize_project(self, project: ConstructionProject, citizens: Dict[str, Citizen]) -> None:
        building = Building(
            building_id=f"building_{project.project_id}",
            name=project.name,
            location=project.location,
            structure_type=project.building_type,
            condition=100,
            owner=None,
            damaged=False,
        )
        self.completed_buildings.append(building)
        city = self.world.get_city(project.location.city)
        if city:
            city.buildings.append(building)
        for worker_id in project.workers:
            citizen = citizens.get(worker_id)
            if citizen:
                citizen.skills.building = min(citizen.skills.building + 2, 100)
                citizen.add_memory(f"Completed construction: {project.name}. Building skill +2.", importance=3)

    def repair_structure(self, building: Building, workers: List[str]) -> None:
        repair_amount = len(workers) * 5
        building.condition = min(100, building.condition + repair_amount)
        if building.condition >= 80:
            building.damaged = False
