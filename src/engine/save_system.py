from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List

from src.engine.citizen import Citizen
from src.engine.world import World, City, Building, Road, Mine, Location


class SaveManager:
    def __init__(self, path: str = "civilization_state.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(str(self.path))
        self.connection.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS citizens (
                citizen_id TEXT PRIMARY KEY,
                name TEXT,
                age INTEGER,
                is_child INTEGER,
                address TEXT,
                city TEXT,
                territory TEXT,
                country TEXT,
                personality TEXT,
                job TEXT,
                balance REAL,
                home TEXT,
                skills TEXT,
                education TEXT,
                relationships TEXT,
                memories TEXT,
                is_in_prison INTEGER,
                active INTEGER
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cities (
                name TEXT PRIMARY KEY,
                territory TEXT,
                country TEXT,
                population INTEGER
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS buildings (
                building_id TEXT PRIMARY KEY,
                name TEXT,
                address TEXT,
                city TEXT,
                territory TEXT,
                country TEXT,
                structure_type TEXT,
                condition INTEGER,
                owner TEXT,
                damaged INTEGER
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS roads (
                road_id TEXT PRIMARY KEY,
                name TEXT,
                start_address TEXT,
                start_city TEXT,
                start_territory TEXT,
                start_country TEXT,
                end_address TEXT,
                end_city TEXT,
                end_territory TEXT,
                end_country TEXT,
                condition INTEGER,
                capacity INTEGER
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS mines (
                mine_id TEXT PRIMARY KEY,
                name TEXT,
                address TEXT,
                city TEXT,
                territory TEXT,
                country TEXT,
                resource_type TEXT,
                yield_rate REAL,
                discovered INTEGER
            )
            """
        )
        self.connection.commit()

    def save_citizens(self, citizens: List[Citizen]) -> None:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM citizens")
        for citizen in citizens:
            record = citizen.to_record()
            cursor.execute(
                """
                INSERT INTO citizens (
                    citizen_id, name, age, is_child, address, city, territory, country,
                    personality, job, balance, home, skills, education, relationships, memories,
                    is_in_prison, active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    record["citizen_id"],
                    record["name"],
                    record["age"],
                    record["is_child"],
                    record["address"],
                    record["city"],
                    record["territory"],
                    record["country"],
                    record["personality"],
                    record["job"],
                    record["balance"],
                    record["home"],
                    record["skills"],
                    record["education"],
                    record["relationships"],
                    record["memories"],
                    record["is_in_prison"],
                    record["active"],
                ],
            )
        self.connection.commit()

    def load_citizens(self) -> List[Citizen]:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM citizens")
        rows = cursor.fetchall()
        return [Citizen.from_record(dict(row)) for row in rows]

    def save_world(self, world: World) -> None:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM cities")
        cursor.execute("DELETE FROM buildings")
        cursor.execute("DELETE FROM roads")
        cursor.execute("DELETE FROM mines")

        for city in world.cities.values():
            cursor.execute(
                "INSERT INTO cities (name, territory, country, population) VALUES (?, ?, ?, ?)",
                [city.name, city.territory, city.country, city.population],
            )
            for building in city.buildings:
                cursor.execute(
                    "INSERT INTO buildings (building_id, name, address, city, territory, country, structure_type, condition, owner, damaged) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        building.building_id,
                        building.name,
                        building.location.address,
                        building.location.city,
                        building.location.territory,
                        building.location.country,
                        building.structure_type,
                        building.condition,
                        building.owner,
                        int(building.damaged),
                    ],
                )
            for road in city.roads:
                cursor.execute(
                    "INSERT INTO roads (road_id, name, start_address, start_city, start_territory, start_country, end_address, end_city, end_territory, end_country, condition, capacity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        road.road_id,
                        road.name,
                        road.start.address,
                        road.start.city,
                        road.start.territory,
                        road.start.country,
                        road.end.address,
                        road.end.city,
                        road.end.territory,
                        road.end.country,
                        road.condition,
                        road.capacity,
                    ],
                )
            for mine in city.mines:
                cursor.execute(
                    "INSERT INTO mines (mine_id, name, address, city, territory, country, resource_type, yield_rate, discovered) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        mine.mine_id,
                        mine.name,
                        mine.location.address,
                        mine.location.city,
                        mine.location.territory,
                        mine.location.country,
                        mine.resource_type,
                        mine.yield_rate,
                        int(mine.discovered),
                    ],
                )
        self.connection.commit()

    def load_world(self) -> World:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM cities")
        world = World(name="Minecraftia", territory="Unknown", country="Minecraftia")
        for row in cursor.fetchall():
            city = City(
                name=row["name"],
                territory=row["territory"],
                country=row["country"],
                population=int(row["population"]),
            )
            world.register_city(city)

        cursor.execute("SELECT * FROM buildings")
        for row in cursor.fetchall():
            location = Location(
                address=row["address"],
                city=row["city"],
                territory=row["territory"],
                country=row["country"],
            )
            building = Building(
                building_id=row["building_id"],
                name=row["name"],
                location=location,
                structure_type=row["structure_type"],
                condition=int(row["condition"]),
                owner=row["owner"],
                damaged=bool(row["damaged"]),
            )
            city = world.get_city(row["city"])
            if city:
                city.buildings.append(building)

        cursor.execute("SELECT * FROM roads")
        for row in cursor.fetchall():
            start = Location(
                address=row["start_address"],
                city=row["start_city"],
                territory=row["start_territory"],
                country=row["start_country"],
            )
            end = Location(
                address=row["end_address"],
                city=row["end_city"],
                territory=row["end_territory"],
                country=row["end_country"],
            )
            road = Road(
                road_id=row["road_id"],
                name=row["name"],
                start=start,
                end=end,
                condition=int(row["condition"]),
                capacity=int(row["capacity"]),
            )
            city = world.get_city(row["start_city"])
            if city:
                city.roads.append(road)

        cursor.execute("SELECT * FROM mines")
        for row in cursor.fetchall():
            location = Location(
                address=row["address"],
                city=row["city"],
                territory=row["territory"],
                country=row["country"],
            )
            mine = Mine(
                mine_id=row["mine_id"],
                name=row["name"],
                location=location,
                resource_type=row["resource_type"],
                yield_rate=float(row["yield_rate"]),
                discovered=bool(row["discovered"]),
            )
            city = world.get_city(row["city"])
            if city:
                city.mines.append(mine)

        return world

    def close(self) -> None:
        self.connection.close()
