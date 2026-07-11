from src.simulation.ai_civilization import AICivilizationSimulator


def test_ai_agent_cycle():
    sim = AICivilizationSimulator(citizen_count=10)
    sim.run(ticks=1)
    assert len(sim.agents) == 10
    assert sim.agents[0].last_decision is not None
    print("✓ AI agent cycle test passed")
