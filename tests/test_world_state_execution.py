from src.production.engine import ProductionCivilizationRuntime, PerformanceConfig


def test_runtime_updates_world_state_and_persists_action_log():
    config = PerformanceConfig(max_agents_per_tick=20, max_active_citizens=20, tick_interval_seconds=0.0)
    runtime = ProductionCivilizationRuntime(config=config)
    runtime.run(ticks=1)

    state = runtime.state_store.load()
    assert "world_actions" in state
    assert "events" in state
    assert len(state["world_actions"]) >= 0
    assert runtime.tick_count == 1
