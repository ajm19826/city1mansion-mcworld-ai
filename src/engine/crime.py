from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.engine.citizen import Citizen
from src.engine.economy import EconomySystem
from src.engine.world import World


@dataclass
class CrimeCase:
    case_id: str
    suspect_id: str
    crime_type: str
    severity: int
    reported_at: str
    resolved: bool = False
    sentence_hours: int = 0


@dataclass
class PrisonRecord:
    citizen_id: str
    crime_type: str
    sentence_hours: int
    start_time: str
    release_time: str
    prison_location: str


@dataclass
class LegalSystem:
    world: World
    economy: EconomySystem
    cases: List[CrimeCase] = field(default_factory=list)
    prison_records: List[PrisonRecord] = field(default_factory=list)

    def detect_crime(self, citizen: Citizen) -> Optional[CrimeCase]:
        chance = 0.0
        if citizen.balance < 0:
            chance += 0.1
        if citizen.job.title == "Business Owner" and citizen.balance > 50000:
            chance += 0.02
        if not citizen.is_child and citizen.job.title == "Construction Worker" and citizen.skills.building < 20:
            chance += 0.01
        if random.random() < chance:
            case = CrimeCase(
                case_id=f"case_{len(self.cases) + 1:04d}",
                suspect_id=citizen.citizen_id,
                crime_type=random.choice(["Theft", "Fraud", "Property Damage", "Illegal Construction"]),
                severity=random.randint(1, 5),
                reported_at=datetime.utcnow().isoformat(),
            )
            self.cases.append(case)
            citizen.add_memory(f"Accused of {case.crime_type}.", importance=3)
            return case
        return None

    def investigate(self) -> None:
        for case in self.cases:
            if not case.resolved and random.random() < 0.5:
                case.resolved = True
                case.sentence_hours = 24 * case.severity

    def adjudicate(self, citizens: Dict[str, Citizen]) -> None:
        for case in self.cases:
            if case.resolved and case.sentence_hours > 0 and not any(record.citizen_id == case.suspect_id for record in self.prison_records):
                citizen = citizens.get(case.suspect_id)
                if citizen:
                    release = datetime.utcnow() + timedelta(hours=case.sentence_hours)
                    record = PrisonRecord(
                        citizen_id=citizen.citizen_id,
                        crime_type=case.crime_type,
                        sentence_hours=case.sentence_hours,
                        start_time=datetime.utcnow().isoformat(),
                        release_time=release.isoformat(),
                        prison_location=f"Prison_{citizen.city}",
                    )
                    self.prison_records.append(record)
                    citizen.is_in_prison = True
                    citizen.add_memory(f"Sentenced to {case.sentence_hours} hours for {case.crime_type}.", importance=4)

    def release_prisoners(self, citizens: Dict[str, Citizen]) -> None:
        now = datetime.utcnow()
        for record in list(self.prison_records):
            release = datetime.fromisoformat(record.release_time)
            if now >= release:
                citizen = citizens.get(record.citizen_id)
                if citizen:
                    citizen.is_in_prison = False
                    citizen.add_memory(f"Released from prison after serving {record.sentence_hours} hours.", importance=3)
                self.prison_records.remove(record)

    def process_crime(self, citizens: List[Citizen]) -> None:
        citizen_lookup = {citizen.citizen_id: citizen for citizen in citizens}
        for citizen in citizens:
            if not citizen.is_in_prison and self.detect_crime(citizen):
                pass
        self.investigate()
        self.adjudicate(citizen_lookup)
