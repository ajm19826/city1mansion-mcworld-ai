from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.engine import SimulationEngine
from src.production.state_store import ProductionStateStore
from src.production.safety import SafetyGuard
from src.simulation.ai_civilization import AICivilizationSimulator


@dataclass
class PerformanceConfig:
    max_agents_per_tick: int = 40
    max_active_citizens: int = 80
    tick_interval_seconds: float = 1.0
    model_call_frequency: int = 50
    use_background_simulation: bool = False


class ProductionCivilizationRuntime:
    def __init__(self, config: Optional[PerformanceConfig] = None, world_path: Optional[str] = None) -> None:
        self.config = config or PerformanceConfig()
        self.sim = AICivilizationSimulator(citizen_count=1000, world_path=world_path)
        self.state_store = ProductionStateStore()
        self.safety_guard = SafetyGuard(max_actions_per_tick=self.config.max_agents_per_tick)
        self.tick_count = 0
        self.running = False

    def run_tick(self) -> None:
        self.tick_count += 1
        self.sim.engine.run_tick()
        self._run_priority_agents()
        if self.tick_count % self.config.model_call_frequency == 0:
            self._run_background_updates()

    def _run_priority_agents(self) -> None:
        active_agents = self.sim.agents[: self.config.max_agents_per_tick]
        for agent in active_agents:
            if random.random() < 0.2:
                context = {
                    "city": agent.state.city,
                    "job": agent.state.job,
                    "balance": agent.state.financial_status,
                    "skills": agent.state.skills,
                    "tick": self.tick_count,
                }
                decision = self.sim.decision_engine.decide(agent, context)
                if not self.safety_guard.validate(decision, agent.state.name):
                    continue
                action = self.sim.minecraft.execute_decision(decision, agent.state.name)
                if action:
                    self.sim.minecraft.publish_action(action)
                    self.state_store.append_action({
                        "agent": agent.state.name,
                        "action_type": action.action_type,
                        "target": action.target,
                        "details": action.details,
                        "tick": self.tick_count,
                    })
                self.state_store.append_event({
                    "agent": agent.state.name,
                    "decision": decision.get("decision"),
                    "tick": self.tick_count,
                })

    def _run_background_updates(self) -> None:
        if self.config.use_background_simulation:
            for agent in self.sim.agents[self.config.max_active_citizens:]:
                agent.memory.add("Background simulation update", importance=1)

    def run(self, ticks: int = 10) -> None:
        self.running = True
        try:
            for _ in range(ticks):
                self.run_tick()
                time.sleep(self.config.tick_interval_seconds)
        finally:
            self.running = False
            self.state_store.append_event({"event": "runtime_stopped", "tick": self.tick_count})

    def stop(self) -> None:
        if self.sim and getattr(self.sim, "plugin_server", None):
            self.sim.plugin_server.stop()
