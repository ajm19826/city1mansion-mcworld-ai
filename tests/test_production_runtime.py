from src.production import ProductionCivilizationRuntime, PerformanceConfig


def test_production_runtime_runs():
    config = PerformanceConfig(max_agents_per_tick=50, max_active_citizens=50, tick_interval_seconds=0.0)
    runtime = ProductionCivilizationRuntime(config=config)
    runtime.run(ticks=2)
    assert runtime.tick_count == 2
    print("✓ Production runtime test passed")
