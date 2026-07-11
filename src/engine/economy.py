from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.engine.citizen import Citizen
from src.engine.world import City


@dataclass
class Business:
    business_id: str
    name: str
    owner_id: Optional[str]
    industry: str
    employees: List[str] = field(default_factory=list)
    revenue: float = 0.0
    expenses: float = 0.0
    active: bool = True

    def run_cycle(self, citizens: Dict[str, Citizen]) -> None:
        employee_count = len(self.employees)
        output = max(0.0, employee_count * random.uniform(500.0, 2500.0))
        self.revenue += output
        self.expenses += employee_count * 250.0
        if employee_count > 0:
            for citizen_id in self.employees:
                citizen = citizens.get(citizen_id)
                if citizen:
                    citizen.balance += citizen.job.salary * 0.01


@dataclass
class Market:
    prices: Dict[str, float] = field(default_factory=lambda: {
        "coal": 12.0,
        "iron": 22.0,
        "gold": 45.0,
        "diamonds": 110.0,
        "stone": 6.0,
        "rare": 90.0,
    })
    demand: Dict[str, float] = field(default_factory=lambda: {
        "coal": 1.0,
        "iron": 1.0,
        "gold": 1.0,
        "diamonds": 1.0,
        "stone": 1.0,
        "rare": 1.0,
    })
    supply: Dict[str, float] = field(default_factory=lambda: {
        "coal": 1.0,
        "iron": 1.0,
        "gold": 1.0,
        "diamonds": 1.0,
        "stone": 1.0,
        "rare": 1.0,
    })

    def update(self) -> None:
        for resource in self.prices:
            self.demand[resource] = max(0.1, self.demand[resource] + random.uniform(-0.05, 0.07))
            self.supply[resource] = max(0.1, self.supply[resource] + random.uniform(-0.05, 0.05))
            self.prices[resource] = max(1.0, self.prices[resource] * (1 + 0.02 * (self.demand[resource] - self.supply[resource])))


@dataclass
class Bank:
    accounts: Dict[str, float] = field(default_factory=dict)

    def get_balance(self, citizen_id: str) -> float:
        return self.accounts.get(citizen_id, 0.0)

    def deposit(self, citizen_id: str, amount: float) -> None:
        self.accounts[citizen_id] = self.get_balance(citizen_id) + amount

    def withdraw(self, citizen_id: str, amount: float) -> bool:
        if self.get_balance(citizen_id) >= amount:
            self.accounts[citizen_id] -= amount
            return True
        return False

    def transfer(self, sender_id: str, receiver_id: str, amount: float) -> bool:
        if self.withdraw(sender_id, amount):
            self.deposit(receiver_id, amount)
            return True
        return False


@dataclass
class EconomySystem:
    market: Market = field(default_factory=Market)
    bank: Bank = field(default_factory=Bank)
    businesses: Dict[str, Business] = field(default_factory=dict)
    tax_rate: float = 0.12

    def register_business(self, business: Business) -> None:
        self.businesses[business.business_id] = business

    def pay_salaries(self, citizens: List[Citizen]) -> None:
        for citizen in citizens:
            if citizen.job.salary > 0 and citizen.job.employer:
                amount = citizen.job.salary / 24
                citizen.balance += amount
                self.bank.deposit(citizen.citizen_id, amount)

    def collect_taxes(self, citizens: List[Citizen]) -> float:
        total_tax = 0.0
        for citizen in citizens:
            if citizen.job.salary > 0:
                tax = citizen.job.salary * self.tax_rate / 365
                if self.bank.withdraw(citizen.citizen_id, tax):
                    total_tax += tax
                    citizen.add_memory(f"Paid {tax:.2f} in taxes.", importance=1)
                elif citizen.balance >= tax:
                    citizen.balance -= tax
                    total_tax += tax
                    citizen.add_memory(f"Paid {tax:.2f} in taxes.", importance=1)
        return total_tax

    def process_businesses(self, citizens: List[Citizen]) -> None:
        citizen_lookup = {citizen.citizen_id: citizen for citizen in citizens}
        for business in self.businesses.values():
            business.run_cycle(citizen_lookup)

    def update_market(self, world_resources: Dict[str, float]) -> None:
        self.market.supply = {resource: max(0.1, world_resources.get(resource, 0.1) / 1000.0) for resource in self.market.supply}
        self.market.update()

    def assign_employer(self, citizen: Citizen, business_id: str) -> None:
        business = self.businesses.get(business_id)
        if business and citizen.citizen_id not in business.employees:
            business.employees.append(citizen.citizen_id)
            citizen.job.employer = business.owner_id

    def import_resources(self, world_resources: Dict[str, float]) -> None:
        for resource, volume in world_resources.items():
            self.market.supply[resource] = max(self.market.supply.get(resource, 0.1), volume / 1000.0)

    def tweak_prices(self) -> None:
        for resource, price in self.market.prices.items():
            self.market.prices[resource] = max(1.0, price * random.uniform(0.98, 1.05))
