from __future__ import annotations

import random
from typing import Dict, List, Optional

from src.engine.ai_manager import AIManager
from src.engine.citizen import Citizen
from src.engine.construction import ConstructionSystem
from src.engine.crime import LegalSystem
from src.engine.economy import EconomySystem
from src.engine.exploration import ExplorationSystem
from src.engine.government import GovernmentSystem
from src.engine.interaction import InteractionSystem
from src.engine.mining import MiningSystem
from src.engine.save_system import SaveManager
from src.engine.war import DiplomacySystem
from src.engine.world import Building, City, Location, Road, World


class SimulationEngine:
    def __init__(self) -> None:
        self.world = World(name="Minecraftia", territory="Minecraftia", country="Minecraftia")
        self.citizens: List[Citizen] = []
        self.save_manager = SaveManager()
        self.ai_manager = AIManager()
        self.economy = EconomySystem()
        self.government = GovernmentSystem(world=self.world)
        self.mining = MiningSystem()
        self.diplomacy = DiplomacySystem(world=self.world)
        self.legal = LegalSystem(world=self.world, economy=self.economy)
        self.construction = ConstructionSystem(world=self.world)
        self.interaction = InteractionSystem()
        self.exploration = ExplorationSystem()
        self.player_location: str = "Monesttery"

    def bootstrap(self, resume: bool = False) -> None:
        self.save_manager.clear_resume()

        if resume and self.save_manager.should_resume():
            loaded_citizens = self.save_manager.load_citizens()
            loaded_world = self.save_manager.load_world()
            if loaded_citizens and loaded_world.cities:
                self.citizens = loaded_citizens
                self.world = loaded_world
                self.government = GovernmentSystem(world=self.world)
                self.legal = LegalSystem(world=self.world, economy=self.economy)
                self.diplomacy = DiplomacySystem(world=self.world)
                self.mining = MiningSystem()
                self.construction = ConstructionSystem(world=self.world)
                self.government.bootstrap_government(self.citizens)
                self.save_manager.clear_resume()
                return

        self._create_world()
        self._create_population()
        self._create_infrastructure()
        self.government.bootstrap_government(self.citizens)
        self._initialize_businesses_and_mines()
        self._initialize_construction_projects()
        self.save_state()

    def _create_world(self) -> None:
        city_names = [
            "Monesttery", "Sand Yusef", "Greenvale", "Ironhold", "Rivergate", "Westbay", "Northwatch",
            "Stoneford", "Eastgate", "Hillview", "Sunfield", "Lakeport", "Cedarvale", "Frostholm",
            "Mossfield", "Oakridge", "Redmarsh", "Silverkeep", "Pinehaven", "Windrest",
        ]
        for name in city_names:
            city = City(name=name, territory="Central", country="Minecraftia")
            self.world.register_city(city)

    def _create_population(self) -> None:
        city_names = list(self.world.cities.keys())
        for index in range(1, 5001):
            city = random.choice(city_names)
            citizen = Citizen.generate_identity(index=index, city=city, territory="Central", country="Minecraftia")
            citizen.active = index <= 250
            self.citizens.append(citizen)
            self.world.cities[city].population += 1

    def _create_infrastructure(self) -> None:
        for city in self.world.cities.values():
            building = Building(
                building_id=f"building_{city.name}_01",
                name=f"{city.name} Townhall",
                location=Location(address=f"1 {city.name} Center", city=city.name, territory=city.territory, country=city.country),
                structure_type="Government",
                condition=random.randint(70, 100),
                owner=None,
            )
            city.buildings.append(building)
            road = Road(
                road_id=f"road_{city.name}_01",
                name=f"Main Road {city.name}",
                start=building.location,
                end=Location(address=f"2 {city.name} East", city=city.name, territory=city.territory, country=city.country),
                condition=random.randint(60, 100),
                capacity=random.randint(50, 150),
            )
            city.roads.append(road)

    def _initialize_businesses_and_mines(self) -> None:
        from src.engine.mining import MiningCompany

        for index, city_name in enumerate(self.world.cities, start=1):
            company_id = f"mineco_{index:03d}"
            company = MiningCompany(
                company_id=company_id,
                name=f"Mining Co. {index}",
                owner_id=None,
            )
            self.mining.register_company(company)
            residents = [citizen.citizen_id for citizen in self.citizens if citizen.city == city_name and not citizen.is_child]
            if residents:
                worker_ids = random.sample(residents, k=min(3, len(residents)))
                self.mining.assign_workers(company_id, worker_ids)
            resource_type = random.choice(["coal", "iron", "gold", "diamonds", "stone", "rare"])
            self.mining.discover_mine(self.world, city_name, resource_type)

    def _initialize_construction_projects(self) -> None:
        for city in self.world.cities.values():
            if random.random() < 0.7:
                project = self.construction.create_project(
                    name=f"{city.name} Public Project",
                    location=Location(address=f"1 {city.name} District", city=city.name, territory=city.territory, country=city.country),
                    building_type=random.choice(["Market", "School", "Hospital", "Library"]),
                    required_skill=random.randint(40, 70),
                )
                workers = random.sample([c.citizen_id for c in self.citizens if c.city == city.name and not c.is_child], k=min(10, len([c for c in self.citizens if c.city == city.name and not c.is_child])))
                self.construction.assign_workers(project.project_id, workers, {c.citizen_id: c for c in self.citizens})

    def run_tick(self) -> None:
        self._run_government()
        self._run_economy()
        self._run_mining()
        self._run_crime()
        self._run_diplomacy()
        self._run_construction()
        self._run_interaction()
        self._run_exploration()

        active_citizens = self.ai_manager.select_active_citizens(self.citizens, player_location=self.player_location)
        for citizen in active_citizens:
            self.ai_manager.run_decision_cycle(citizen)

        self._background_simulation()
        self.save_state()

    def _run_government(self) -> None:
        for city in self.world.cities.values():
            self.government.enforce_policy(city.name)

    def _run_economy(self) -> None:
        self.economy.update_market(self.world.resources)
        self.economy.process_businesses(self.citizens)
        self.economy.collect_taxes(self.citizens)

    def _run_mining(self) -> None:
        self.mining.mine_resources(self.world)
        self.economy.import_resources(self.world.resources)

    def _run_crime(self) -> None:
        self.legal.process_crime(self.citizens)
        self.legal.release_prisoners({citizen.citizen_id: citizen for citizen in self.citizens})

    def _run_diplomacy(self) -> None:
        self.diplomacy.resolve_conflicts()
        self.diplomacy.balance_power()

    def _run_construction(self) -> None:
        citizen_lookup = {citizen.citizen_id: citizen for citizen in self.citizens}
        self.construction.run_projects(citizen_lookup)
        damaged = self.construction.discover_damaged_structure(self.world)
        if damaged:
            workers = random.sample([c.citizen_id for c in self.citizens if c.skills.building > 30], k=min(5, len([c for c in self.citizens if c.skills.building > 30])))
            self.construction.repair_structure(damaged, workers)

    def _run_interaction(self) -> None:
        self.interaction.process_social_interactions(self.citizens)
        self.interaction.strengthen_relationships(self.citizens)

    def _run_exploration(self) -> None:
        self.exploration.process_explorations(self.citizens, self.world)

    def _background_simulation(self) -> None:
        for citizen in self.citizens[250:500]:
            if random.random() < 0.15:
                citizen.add_memory("Checked routine schedule.", importance=1)

    def save_state(self) -> None:
        self.save_manager.save_state(self.world, self.citizens)

    def shutdown(self) -> None:
        self.save_manager.close()
