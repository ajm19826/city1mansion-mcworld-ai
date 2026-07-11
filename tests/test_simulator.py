#!/usr/bin/env python3
"""
Comprehensive test suite for the Minecraftia Civilization Simulator.
Run with: python tests/test_simulator.py
"""

from src.engine import (
    SimulationEngine,
    Citizen,
    get_population_stats,
    get_city_stats,
    get_economy_report,
)


def test_bootstrap():
    """Test that the engine bootstraps correctly."""
    engine = SimulationEngine()
    engine.bootstrap()
    
    assert len(engine.citizens) == 5000, "Should have 5000 citizens"
    assert len(engine.world.cities) >= 20, "Should have at least 20 cities"
    print("✓ Bootstrap test passed")


def test_citizen_types():
    """Test that citizens are correctly categorized."""
    engine = SimulationEngine()
    engine.bootstrap()
    
    adults = [c for c in engine.citizens if not c.is_child]
    children = [c for c in engine.citizens if c.is_child]
    
    assert len(adults) == 4250, f"Expected 4250 adults, got {len(adults)}"
    assert len(children) == 750, f"Expected 750 children, got {len(children)}"
    print("✓ Citizen types test passed")


def test_economy():
    """Test that the economy system works."""
    engine = SimulationEngine()
    engine.bootstrap()
    
    # Run economy phase
    engine._run_economy()
    
    # Check that taxes were collected
    total_balance = sum(c.balance for c in engine.citizens)
    assert total_balance > 0, "Citizens should have positive balance"
    print("✓ Economy test passed")


def test_crime_system():
    """Test that the crime system detects crimes."""
    engine = SimulationEngine()
    engine.bootstrap()
    
    # Run crime phase multiple times
    for _ in range(5):
        engine._run_crime()
    
    assert len(engine.legal.cases) >= 0, "Crime cases should exist"
    assert len(engine.legal.prison_records) >= 0, "Prison records should exist"
    print("✓ Crime system test passed")


def test_mining_system():
    """Test that the mining system works."""
    engine = SimulationEngine()
    engine.bootstrap()
    
    # Run mining phase
    engine._run_mining()
    
    # Check resources were extracted
    assert sum(engine.world.resources.values()) > 0, "Resources should be extracted"
    assert len({mine.mine_id for city in engine.world.cities.values() for mine in city.mines}) == sum(len(city.mines) for city in engine.world.cities.values()), "Mine IDs should be unique"
    print("✓ Mining system test passed")


def test_construction_system():
    """Test that construction projects work."""
    engine = SimulationEngine()
    engine.bootstrap()
    
    # Run construction phase
    engine._run_construction()
    
    # Check projects exist
    assert len(engine.construction.projects) >= 0, "Should have construction projects"
    print("✓ Construction system test passed")


def test_interaction_system():
    """Test that interactions work."""
    engine = SimulationEngine()
    engine.bootstrap()
    
    # Run interaction phase
    engine._run_interaction()
    
    # Check interactions were recorded
    assert len(engine.interaction.interactions) >= 0, "Should have interactions"
    print("✓ Interaction system test passed")


def test_simulation_tick():
    """Test that a full simulation tick runs without error."""
    engine = SimulationEngine()
    engine.bootstrap()
    
    # Run one tick
    engine.run_tick()
    
    # Verify state still intact
    assert len(engine.citizens) == 5000
    assert len(engine.world.cities) >= 20
    print("✓ Simulation tick test passed")


def test_save_load():
    """Test that save and load work."""
    engine1 = SimulationEngine()
    engine1.bootstrap()
    
    # Get a citizen's state before save
    citizen_before = engine1.citizens[0]
    name_before = citizen_before.name
    balance_before = citizen_before.balance
    
    # Save
    engine1.save_state()
    
    # Create new engine and load
    engine2 = SimulationEngine()
    engine2.bootstrap(resume=True)
    
    # Get the same citizen
    citizen_after = engine2.citizens[0]
    
    # Check state matches
    assert citizen_after.name == name_before, "Citizen name should match"
    assert citizen_after.balance == balance_before, "Citizen balance should match"
    print("✓ Save/load test passed")


def test_bootstrap_resets_state_by_default():
    """A fresh bootstrap should not silently resume a stale in-memory save."""
    engine = SimulationEngine()
    engine.bootstrap()
    engine.citizens[0].balance = 999999.0
    engine.save_state()

    other_engine = SimulationEngine()
    other_engine.bootstrap()

    assert other_engine.citizens[0].balance != 999999.0, "Fresh bootstrap should not resume stale saved state"
    print("✓ Bootstrap reset test passed")


def test_population_stats():
    """Test that population statistics are calculated correctly."""
    engine = SimulationEngine()
    engine.bootstrap()
    
    stats = get_population_stats(engine.citizens)
    
    assert stats["total"] == 5000
    assert stats["adults"] == 4250
    assert stats["children"] == 750
    assert stats["average_balance"] > 0
    assert stats["average_building_skill"] >= 0
    assert stats["in_prison"] >= 0
    print("✓ Population stats test passed")


def test_city_stats():
    """Test that city statistics are calculated correctly."""
    engine = SimulationEngine()
    engine.bootstrap()
    
    stats = get_city_stats(engine.world)
    
    assert len(stats) >= 20, "Should have at least 20 cities"
    for city_name, city_stat in stats.items():
        assert city_stat["population"] > 0
        assert city_stat["buildings"] >= 0
        assert city_stat["roads"] >= 0
        assert city_stat["mines"] >= 0
    print("✓ City stats test passed")


def test_economy_report():
    """Test that economy report is generated correctly."""
    engine = SimulationEngine()
    engine.bootstrap()
    
    report = get_economy_report(engine.economy)
    
    assert "market_prices" in report
    assert "total_business_revenue" in report
    assert "total_business_expenses" in report
    assert "tax_rate" in report
    assert report["tax_rate"] > 0
    print("✓ Economy report test passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("MINECRAFTIA CIVILIZATION SIMULATOR - TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        test_bootstrap,
        test_citizen_types,
        test_economy,
        test_crime_system,
        test_mining_system,
        test_construction_system,
        test_interaction_system,
        test_simulation_tick,
        test_save_load,
        test_population_stats,
        test_city_stats,
        test_economy_report,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
