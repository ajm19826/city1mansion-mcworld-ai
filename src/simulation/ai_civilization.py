from __future__ import annotations

from typing import List

from src.ai import CitizenAgent, AgentState, DecisionEngine
from src.ai.roles import MayorAgent, ConstructionAgent, ExplorerAgent, EconomyAgent
from src.engine import SimulationEngine
from src.minecraft import MinecraftIntegration, MinecraftAction, MinecraftBridge, MinecraftPluginHook
from src.world_actions import WorldActionExecutor


class AICivilizationSimulator:
    def __init__(self, citizen_count: int = 10) -> None:
        self.engine = SimulationEngine()
        self.engine.bootstrap()
        self.decision_engine = DecisionEngine(model_enabled=False)
        self.minecraft = MinecraftIntegration(enabled=True)
        self.minecraft.connect()
        self.bridge = MinecraftBridge(world_path=self.minecraft.world_path)
        self.plugin_hook = MinecraftPluginHook(world_path=self.minecraft.world_path)
        self.world_actions = WorldActionExecutor()
        self.agents: List[CitizenAgent] = []
        self._create_agents(citizen_count)

    def _create_agents(self, citizen_count: int) -> None:
        for citizen in self.engine.citizens[:citizen_count]:
            state = AgentState(
                name=citizen.name,
                role=citizen.job.title,
                city=citizen.city,
                job=citizen.job.title,
                personality=citizen.personality,
                skills={
                    "building": citizen.skills.building,
                    "mining": citizen.skills.mining,
                    "driving": citizen.skills.driving,
                },
                financial_status=citizen.balance,
                location=citizen.city,
                history=["Initialized from simulation"],
            )
            if "mayor" in citizen.job.title.lower() or citizen.city == "Monesttery" and citizen.balance > 50000:
                self.agents.append(MayorAgent(state))
            elif "construction" in citizen.job.title.lower() or citizen.skills.building > 70:
                self.agents.append(ConstructionAgent(state))
            elif "miner" in citizen.job.title.lower() or citizen.skills.mining > 60:
                self.agents.append(ExplorerAgent(state))
            elif "business" in citizen.job.title.lower() or citizen.balance > 40000:
                self.agents.append(EconomyAgent(state))
            else:
                self.agents.append(CitizenAgent(state))

    def run_agent_cycle(self) -> None:
        for agent in self.agents:
            context = {
                "city": agent.state.city,
                "job": agent.state.job,
                "balance": agent.state.financial_status,
                "skills": agent.state.skills,
            }
            decision = self.decision_engine.decide(agent, context)
            agent.memory.add(f"Decision: {decision['decision']}", importance=2)
            action = self.minecraft.execute_decision(decision, agent.state.name)
            if action:
                self.minecraft.publish_action(action)
                entity_id = f"entity_{agent.state.name.replace(' ', '_').lower()}"
                self.plugin_hook.register_entity(entity_id, agent.state.name, agent.state.role, agent.state.city)
                if action.action_type == "build":
                    self.bridge.emit_build_command(agent.state.name, agent.state.city)
                    self.plugin_hook.queue_action(entity_id, "build", {"location": agent.state.city, "block": "oak_planks"})
                elif action.action_type == "explore":
                    self.bridge.emit_explore_command(agent.state.name, agent.state.city)
                    self.plugin_hook.queue_action(entity_id, "explore", {"location": agent.state.city})
                elif action.action_type == "government":
                    self.bridge.emit_govern_command(agent.state.name, "fund_repairs")
                    self.plugin_hook.queue_action(entity_id, "govern", {"action": "fund_repairs"})
                elif action.action_type == "economy":
                    self.bridge.emit_economy_command(agent.state.name, "adjust_prices")
                    self.plugin_hook.queue_action(entity_id, "economy", {"item": "emerald", "count": 1})
                self.plugin_hook.process_tick()
            world_action = self.world_actions.execute(decision, agent.state.name, self.engine.world)
            if world_action:
                agent.memory.add(f"World action: {world_action.action_type}", importance=2)
            if agent.state.role == "Mayor":
                agent.remember("Handled city governance decision", importance=4, long_term=True)
            elif agent.state.role == "Construction Agent":
                agent.remember("Handled construction planning", importance=3, long_term=True)
            elif agent.state.role == "Explorer":
                agent.remember("Explored territory for opportunities", importance=3, long_term=True)
            elif agent.state.role == "Economy Manager":
                agent.remember("Managed trade or business posture", importance=4, long_term=True)

    def run(self, ticks: int = 1) -> None:
        for _ in range(ticks):
            self.engine.run_tick()
            self.run_agent_cycle()
