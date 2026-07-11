"""Utility functions and helpers for the Minecraftia Civilization Simulator."""

from typing import Dict, List, Optional
from src.engine.citizen import Citizen
from src.engine.world import World, City


def get_population_stats(citizens: List[Citizen]) -> Dict:
    """Get population demographics."""
    total = len(citizens)
    adults = len([c for c in citizens if not c.is_child])
    children = len([c for c in citizens if c.is_child])
    avg_balance = sum(c.balance for c in citizens) / total if total > 0 else 0
    avg_skill_building = sum(c.skills.building for c in citizens) / total if total > 0 else 0
    
    return {
        "total": total,
        "adults": adults,
        "children": children,
        "average_balance": round(avg_balance, 2),
        "average_building_skill": round(avg_skill_building, 1),
        "in_prison": len([c for c in citizens if c.is_in_prison]),
    }


def get_city_stats(world: World) -> Dict:
    """Get statistics for all cities."""
    stats = {}
    for city_name, city in world.cities.items():
        stats[city_name] = {
            "population": city.population,
            "buildings": len(city.buildings),
            "roads": len(city.roads),
            "mines": len(city.mines),
            "mayor": world.governments[city_name].mayor if city_name in world.governments else None,
        }
    return stats


def get_economy_report(economy) -> Dict:
    """Get economy system report."""
    total_revenue = sum(b.revenue for b in economy.businesses.values())
    total_expenses = sum(b.expenses for b in economy.businesses.values())
    
    return {
        "market_prices": economy.market.prices.copy(),
        "total_business_revenue": round(total_revenue, 2),
        "total_business_expenses": round(total_expenses, 2),
        "tax_rate": economy.tax_rate,
        "active_businesses": len([b for b in economy.businesses.values() if b.active]),
    }


def find_citizen_by_name(citizens: List[Citizen], name: str) -> Optional[Citizen]:
    """Find a citizen by name."""
    for citizen in citizens:
        if citizen.name.lower() == name.lower():
            return citizen
    return None


def find_citizens_by_job(citizens: List[Citizen], job_title: str) -> List[Citizen]:
    """Find all citizens with a specific job."""
    return [c for c in citizens if c.job.title.lower() == job_title.lower()]


def find_citizens_by_city(citizens: List[Citizen], city_name: str) -> List[Citizen]:
    """Find all citizens in a specific city."""
    return [c for c in citizens if c.city.lower() == city_name.lower()]


def calculate_city_wealth(citizens: List[Citizen], city_name: str) -> float:
    """Calculate total wealth (citizen balances) in a city."""
    city_citizens = find_citizens_by_city(citizens, city_name)
    return sum(c.balance for c in city_citizens)


def get_highest_skill_citizens(citizens: List[Citizen], skill_name: str, count: int = 10) -> List[Citizen]:
    """Get the citizens with highest skill in a given category."""
    skill_map = {
        "building": lambda c: c.skills.building,
        "mining": lambda c: c.skills.mining,
        "driving": lambda c: c.skills.driving,
        "teaching": lambda c: c.skills.teaching,
        "diplomacy": lambda c: c.skills.diplomacy,
        "farming": lambda c: c.skills.farming,
    }
    
    getter = skill_map.get(skill_name.lower())
    if not getter:
        return []
    
    sorted_citizens = sorted(citizens, key=getter, reverse=True)
    return sorted_citizens[:count]


def print_citizen_info(citizen: Citizen) -> str:
    """Format citizen information as a readable string."""
    lines = [
        f"=== {citizen.name} ({citizen.citizen_id}) ===",
        f"Age: {citizen.age} | Type: {'Child' if citizen.is_child else 'Adult'}",
        f"Location: {citizen.address}, {citizen.city}, {citizen.territory}",
        f"Job: {citizen.job.title} (${citizen.job.salary:,.0f}/year)",
        f"Balance: ${citizen.balance:,.2f}",
        f"Skills: Building={citizen.skills.building}, Mining={citizen.skills.mining}, Driving={citizen.skills.driving}",
        f"Education: {citizen.education}",
        f"Relationships: {len(citizen.relationships)} | Memories: {len(citizen.memories)}",
        f"Status: {'IN PRISON' if citizen.is_in_prison else 'Free'} | Active: {citizen.active}",
    ]
    return "\n".join(lines)
