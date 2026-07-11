from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.engine.citizen import Citizen


@dataclass
class Interaction:
    interaction_id: str
    initiator_id: str
    target_id: str
    interaction_type: str
    timestamp: str
    result: Optional[str] = None


@dataclass
class InteractionSystem:
    interactions: List[Interaction] = field(default_factory=list)

    def initiate_interaction(self, initiator: Citizen, target: Citizen, interaction_type: str) -> Interaction:
        from datetime import datetime

        interaction = Interaction(
            interaction_id=f"interaction_{len(self.interactions) + 1:04d}",
            initiator_id=initiator.citizen_id,
            target_id=target.citizen_id,
            interaction_type=interaction_type,
            timestamp=datetime.utcnow().isoformat(),
        )
        self.interactions.append(interaction)
        initiator.add_memory(f"Interacted with {target.name} ({interaction_type}).", importance=1)
        return interaction

    def process_conversation(self, initiator: Citizen, target: Citizen) -> bool:
        interaction = self.initiate_interaction(initiator, target, "Conversation")
        if random.random() > 0.3:
            relationship_exists = any(
                r.citizen_id == target.citizen_id for r in initiator.relationships
            )
            if not relationship_exists:
                initiator.add_relationship(target.citizen_id, "acquaintance", strength=5)
                target.add_relationship(initiator.citizen_id, "acquaintance", strength=5)
                interaction.result = "New friendship formed"
            else:
                initiator.add_memory(f"Talked with {target.name}.", importance=1)
                interaction.result = "Conversation successful"
            return True
        return False

    def process_trade(self, seller: Citizen, buyer: Citizen, amount: float) -> bool:
        interaction = self.initiate_interaction(seller, buyer, "Trade")
        if buyer.balance >= amount:
            buyer.balance -= amount
            seller.balance += amount
            seller.add_memory(f"Sold item to {buyer.name} for {amount:.2f}.", importance=2)
            buyer.add_memory(f"Bought item from {seller.name} for {amount:.2f}.", importance=2)
            interaction.result = f"Trade successful: {amount:.2f} transferred"
            return True
        interaction.result = "Trade failed: insufficient funds"
        return False

    def process_social_interactions(self, citizens: List[Citizen]) -> None:
        if len(citizens) < 2:
            return
        for _ in range(min(50, len(citizens) // 100)):
            initiator = random.choice(citizens)
            target = random.choice([c for c in citizens if c.citizen_id != initiator.citizen_id])
            if random.random() < 0.6:
                self.process_conversation(initiator, target)
            else:
                amount = random.uniform(100.0, 5000.0)
                self.process_trade(initiator, target, amount)

    def strengthen_relationships(self, citizens: List[Citizen]) -> None:
        for citizen in citizens:
            for relationship in citizen.relationships:
                relationship.strength = min(100, relationship.strength + random.randint(0, 2))
