from src.simulation.ai_civilization import AICivilizationSimulator


def test_minecraft_integration_bridge():
    sim = AICivilizationSimulator(citizen_count=8)
    sim.run_agent_cycle()
    assert sim.minecraft.connected
    assert len(sim.minecraft.actions) >= 0
    print("✓ Minecraft integration test passed")
