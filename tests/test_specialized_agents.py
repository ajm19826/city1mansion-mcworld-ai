from src.simulation.ai_civilization import AICivilizationSimulator


def test_specialized_agents_are_created():
    sim = AICivilizationSimulator(citizen_count=12)
    assert len(sim.agents) == 12
    roles = {agent.state.role for agent in sim.agents}
    assert roles
    print("✓ Specialized agents test passed")
