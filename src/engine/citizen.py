from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class SkillSet:
    building: int = 0
    mining: int = 0
    driving: int = 0
    teaching: int = 0
    diplomacy: int = 0
    farming: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            "building": self.building,
            "mining": self.mining,
            "driving": self.driving,
            "teaching": self.teaching,
            "diplomacy": self.diplomacy,
            "farming": self.farming,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "SkillSet":
        return cls(
            building=data.get("building", 0),
            mining=data.get("mining", 0),
            driving=data.get("driving", 0),
            teaching=data.get("teaching", 0),
            diplomacy=data.get("diplomacy", 0),
            farming=data.get("farming", 0),
        )


@dataclass
class Memory:
    timestamp: str
    event: str
    importance: int

    @classmethod
    def create(cls, event: str, importance: int = 1) -> "Memory":
        return cls(timestamp=datetime.utcnow().isoformat(), event=event, importance=importance)


@dataclass
class Relationship:
    citizen_id: str
    relation: str
    strength: int


@dataclass
class Job:
    title: str
    salary: float
    employer: Optional[str] = None


@dataclass
class Citizen:
    citizen_id: str
    name: str
    age: int
    is_child: bool
    address: str
    city: str
    territory: str
    country: str
    personality: str
    job: Job
    balance: float
    home: str
    skills: SkillSet
    education: str
    relationships: List[Relationship] = field(default_factory=list)
    memories: List[Memory] = field(default_factory=list)
    is_in_prison: bool = False
    active: bool = False

    def to_record(self) -> Dict:
        return {
            "citizen_id": self.citizen_id,
            "name": self.name,
            "age": self.age,
            "is_child": self.is_child,
            "address": self.address,
            "city": self.city,
            "territory": self.territory,
            "country": self.country,
            "personality": self.personality,
            "job": json.dumps(self.job.__dict__),
            "balance": self.balance,
            "home": self.home,
            "skills": json.dumps(self.skills.to_dict()),
            "education": self.education,
            "relationships": json.dumps([r.__dict__ for r in self.relationships]),
            "memories": json.dumps([m.__dict__ for m in self.memories]),
            "is_in_prison": int(self.is_in_prison),
            "active": int(self.active),
        }

    @classmethod
    def from_record(cls, record: Dict) -> "Citizen":
        job_data = json.loads(record["job"])
        skills_data = json.loads(record["skills"])
        relationships = [Relationship(**rel) for rel in json.loads(record["relationships"])]
        memories = [Memory(**mem) for mem in json.loads(record["memories"])]

        return cls(
            citizen_id=record["citizen_id"],
            name=record["name"],
            age=int(record["age"]),
            is_child=bool(record["is_child"]),
            address=record["address"],
            city=record["city"],
            territory=record["territory"],
            country=record["country"],
            personality=record["personality"],
            job=Job(**job_data),
            balance=float(record["balance"]),
            home=record["home"],
            skills=SkillSet.from_dict(skills_data),
            education=record["education"],
            relationships=relationships,
            memories=memories,
            is_in_prison=bool(record["is_in_prison"]),
            active=bool(record["active"]),
        )

    def add_memory(self, event: str, importance: int = 1) -> None:
        self.memories.append(Memory.create(event, importance))
        if len(self.memories) > 30:
            self.memories = self.memories[-30:]

    def add_relationship(self, citizen_id: str, relation: str, strength: int = 10) -> None:
        self.relationships.append(Relationship(citizen_id=citizen_id, relation=relation, strength=strength))

    @staticmethod
    def generate_identity(index: int, city: str, territory: str, country: str) -> "Citizen":
        name = f"Citizen_{index:04d}"
        age = random.randint(6, 16) if index > 4250 else random.randint(18, 70)
        is_child = age < 18
        personality = random.choice(["practical", "curious", "ambitious", "empathetic", "disciplined"])
        job_title = "Student" if is_child else random.choice([
            "Construction Worker",
            "Miner",
            "Teacher",
            "Engineer",
            "Business Owner",
            "Police Officer",
            "Farmer",
            "Government Official",
        ])
        salary = 15000.0 if is_child else random.uniform(25000.0, 120000.0)
        return Citizen(
            citizen_id=f"citizen_{index:04d}",
            name=name,
            age=age,
            is_child=is_child,
            address=f"{index} {city} Rd",
            city=city,
            territory=territory,
            country=country,
            personality=personality,
            job=Job(title=job_title, salary=salary),
            balance=round(random.uniform(1000.0, 200000.0), 2),
            home=f"House_{index:04d}",
            skills=SkillSet(
                building=random.randint(10, 95) if not is_child else random.randint(1, 40),
                mining=random.randint(5, 80) if not is_child else random.randint(1, 30),
                driving=random.randint(10, 85) if not is_child else random.randint(1, 25),
                teaching=random.randint(10, 90) if not is_child else random.randint(1, 30),
                diplomacy=random.randint(10, 90) if not is_child else random.randint(1, 35),
                farming=random.randint(10, 80) if not is_child else random.randint(1, 25),
            ),
            education="Primary School" if is_child else random.choice(["High School", "University", "Trade School"]),
        )
