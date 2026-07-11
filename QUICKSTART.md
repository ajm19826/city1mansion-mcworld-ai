# Quick Start Guide - Minecraftia Civilization Simulator

## What Is This?

A sophisticated AI civilization engine for Minecraft. Manage 5,000 autonomous citizens with jobs, relationships, crimes, wars, and dynamic economies—all inside your Minecraft world.

## Installation

```bash
# Clone the repository
git clone https://github.com/ajm19826/city1mansion-mcworld-ai.git
cd city1mansion-mcworld-ai

# Install
python -m pip install -e .
```

## Run the Simulator

### Option 1: Start the Full Game Loop
```bash
python -m src.main
```
This runs indefinitely, auto-saving every tick. Stop with Ctrl+C.

### Option 2: Run for a Fixed Number of Ticks
```python
from src.engine.gameloop import GameLoop

loop = GameLoop(tick_rate=0.5)
loop.run_for_ticks(100)  # Run 100 ticks
```

### Option 3: Programmatic Access
```python
from src.engine import SimulationEngine, get_population_stats, find_citizen_by_name

engine = SimulationEngine()
engine.bootstrap()

# Get a citizen
citizen = find_citizen_by_name(engine.citizens, "Citizen_0001")
print(f"Name: {citizen.name}, Job: {citizen.job.title}, Balance: ${citizen.balance:,.2f}")

# Get stats
stats = get_population_stats(engine.citizens)
print(f"Total: {stats['total']}, Average Wealth: ${stats['average_balance']:,.2f}")

# Run 10 ticks
for _ in range(10):
    engine.run_tick()

engine.save_state()
```

## File Output

After running, you'll have:
- `civilization_state.db` - SQLite database with all game state
- `__pycache__/` - Python bytecode (can be deleted)

## Database Structure

The SQLite database contains:
- **citizens** - All 5,000 agents with job, balance, skills, memories
- **cities** - 20 cities with population and government
- **buildings** - Structures, conditions, ownership
- **roads** - Transportation networks
- **mines** - Resource deposits and discovery status

## Key Statistics

After bootstrapping and running, you'll see:
- **Population**: 5,000 (4,250 adults, 750 children)
- **Cities**: 20 distinct locations
- **Jobs**: 10+ job types with salary ranges
- **Resources**: 6 types (coal, iron, gold, diamonds, stone, rare)
- **Market Prices**: Dynamic based on supply/demand

## System Features

### Economy
- Citizens earn salaries based on job type
- Tax system (12% default rate)
- Market prices fluctuate with supply/demand
- Businesses hire workers and generate revenue

### Government
- Each city has elected mayor and governor
- Police forces for law enforcement
- Building permits (approval required for construction)
- City planning and policy

### Crime
- Crimes detected based on financial desperation
- Investigation → trial → sentencing pipeline
- Prison system with release dates
- 4 crime types: Theft, Fraud, Property Damage, Illegal Construction

### Social
- Citizens form friendships through conversations
- Trade relationships with money exchange
- Relationship strength increases over time
- Memory system tracks important events

### Mining
- Mining companies in each city
- Resource extraction based on worker count
- Yield rates for different resources
- Integration with economy

### Construction
- Construction projects in each city
- Worker assignment and skill progression
- Building types: Markets, Schools, Hospitals, Libraries
- Damaged building detection and repair

### Exploration
- Citizens discover mines and resources
- Exploration skill development
- Discovery database and reporting

### War & Diplomacy
- Inter-city conflicts and territory changes
- Alliance formation
- Conflict resolution mechanics

## Monitoring

Get current stats anytime:

```python
from src.engine import get_population_stats, get_city_stats, get_economy_report

# Population demographics
pop = get_population_stats(engine.citizens)
print(f"In Prison: {pop['in_prison']}")

# City details
cities = get_city_stats(engine.world)
for name, stats in cities.items():
    print(f"{name}: {stats['population']} citizens")

# Economy
econ = get_economy_report(engine.economy)
print(f"Prices: {econ['market_prices']}")
```

## Performance Tips

1. **Increase Tick Rate** for faster simulation:
   ```python
   GameLoop(tick_rate=0.1)  # 0.1s per tick (10 ticks/second)
   ```

2. **Reduce Active Citizens** in AI Manager for lower CPU:
   - Edit `ai_manager.py`, reduce 250 to lower number

3. **Disable Minecraft Connector** for offline mode:
   - Edit `gameloop.py`, comment out `connector.connect()`

## Next Steps

1. **Integrate with Minecraft Server**
   - Implement Paper/Fabric plugin bridge
   - Sync NPC positions and actions

2. **Add LLM Inference**
   - Replace stubs in `ai_manager.py` with real model calls
   - Use local LLMs (Ollama, LM Studio) for privacy

3. **Extend Features**
   - Agriculture and farming
   - Transportation systems
   - Cultural factions
   - Natural disasters

## Troubleshooting

**Issue**: SQLite database error on startup
- **Solution**: Delete `civilization_state.db` and restart (creates fresh world)

**Issue**: Slow performance
- **Solution**: Reduce `tick_rate`, decrease active citizen count

**Issue**: Memory usage too high
- **Solution**: Reduce citizen count from 5,000 in `simulation.py`

**Issue**: Minecraft connector won't connect
- **Solution**: Start game loop without Minecraft: `GameLoop(tick_rate=0.5).run_for_ticks(100)`

## Architecture Overview

```
GameLoop (main entry point)
  ↓
SimulationEngine (core orchestrator)
  ├─ AIManager (citizen decisions)
  ├─ EconomySystem (market, bank, business)
  ├─ GovernmentSystem (permits, policy)
  ├─ LegalSystem (crime, trials, prison)
  ├─ MiningSystem (resource extraction)
  ├─ ConstructionSystem (building projects)
  ├─ InteractionSystem (social dynamics)
  ├─ ExplorationSystem (discovery)
  ├─ DiplomacySystem (war, alliances)
  └─ SaveManager (SQLite persistence)
```

For full architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md).

## License

MIT

## Contributing

Contributions welcome! Areas for contribution:
- Performance optimization
- Minecraft plugin development
- New subsystems
- Testing and stability
- Documentation

## Questions?

Refer to:
- [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- [README.md](README.md) for project overview
- Code comments for implementation details
