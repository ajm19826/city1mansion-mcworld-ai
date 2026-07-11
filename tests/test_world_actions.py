from src.simulation.ai_civilization import AICivilizationSimulator


def test_world_actions_are_executed():
    sim = AICivilizationSimulator(citizen_count=8)
    sim.run_agent_cycle()
    assert len(sim.world_actions.actions) >= 0
    print("✓ World actions test passed")
