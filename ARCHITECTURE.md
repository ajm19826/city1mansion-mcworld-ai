# Minecraftia Civilization Simulator - Architecture Guide

## Overview

The Civilization Simulator is a modular AI engine that manages 5,000 autonomous agents inside a Minecraft world. It handles economies, governments, crime, wars, construction, and social dynamics.

## System Architecture

```
┌──────────────────────────────────────┐
│         Game Loop                     │
│  - Detects player location           │
│  - Runs ticks at 0.5s intervals      │
│  - Saves to SQLite                   │
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│    Simulation Engine (Main)           │
│  - Coordinates all subsystems        │
│  - Runs AI decision cycles           │
│  - Persists game state               │
└──────────────┬───────────────────────┘
               │
    ┌──────────┴──────────┬──────────────┐
    │                     │              │
┌───▼────┐  ┌────────┐  ┌▼──────┐  ┌───▼────┐
│ AI Mgr │  │Economy │  │Gov    │  │Mining  │
└────────┘  └────────┘  └───────┘  └────────┘

┌──────────┐  ┌────────┐  ┌──────────┐  ┌────────┐
│Crime Sys │  │War/Dip │  │Construct │  │Interact│
└──────────┘  └────────┘  └──────────┘  └────────┘

┌──────────────────────────────────────┐
│    Persistent Storage (SQLite)        │
│  - Citizens, Cities, Buildings        │
│  - Roads, Mines, State                │
└──────────────────────────────────────┘
```

## Core Components

### 1. SimulationEngine (`simulation.py`)

**Responsibilities:**
- Bootstrap world and population (5,000 citizens, 20 cities)
- Coordinate subsystem ticks
- Manage player detection
- Orchestrate save/load cycle

**Key Methods:**
- `bootstrap()` - Initialize or load saved state
- `run_tick()` - Execute one simulation step
- `save_state()` - Persist to database
- `shutdown()` - Graceful teardown

### 2. GameLoop (`gameloop.py`)

**Responsibilities:**
- Main execution loop (blocks until stopped)
- Detect player presence
- Execute ticks at fixed intervals
- Handle graceful shutdown

**Key Methods:**
- `run()` - Infinite game loop
- `run_for_ticks(count)` - Run for N ticks
- `bootstrap()` - Load/create civilization
- `shutdown()` - Save and cleanup

### 3. AI Manager (`ai_manager.py`)

**Responsibilities:**
- Select active citizens (250 near player, rest background)
- Run decision cycles for each active citizen
- Model selection (750M for adults, 300M for children)
- Estimate resource usage

**Key Methods:**
- `select_active_citizens()` - Priority queue by proximity
- `run_decision_cycle()` - Execute citizen decisions
- `_adult_decision()` - Adult-specific logic
- `_child_decision()` - Child learning and skill growth

### 4. Citizen Model (`citizen.py`)

**Data Structure:**
```python
Citizen:
  - citizen_id: str (unique identifier)
  - name, age, is_child
  - address, city, territory, country
  - personality: str (practical, curious, ambitious, empathetic, disciplined)
  - job: Job (title, salary, employer)
  - balance: float (bank account)
  - home: str (house identifier)
  - skills: SkillSet (building, mining, driving, teaching, diplomacy, farming)
  - education: str (Primary, High School, University, Trade)
  - relationships: List[Relationship] (with strength)
  - memories: List[Memory] (last 30 events)
  - is_in_prison: bool
  - active: bool (near player or high importance)
```

### 5. Economy System (`economy.py`)

**Components:**
- **Market**: Price/supply/demand curves for 6 resources
- **Bank**: Account management, deposits, withdrawals, transfers
- **Business**: Revenue generation, employee management
- **Taxes**: Salary-based collection at 12% rate

**Key Methods:**
- `pay_salaries()` - Monthly income distribution
- `collect_taxes()` - Tax processing
- `process_businesses()` - Revenue/expense cycles
- `update_market()` - Price adjustments based on supply/demand

### 6. Government System (`government.py`)

**Features:**
- Mayor and governor election
- Police force assignment
- Building permits (80% approval rate)
- City planning and policy enforcement

**Key Methods:**
- `bootstrap_government()` - Assign leaders
- `request_build_permit()` - Process construction requests
- `review_city_plan()` - Approve/reject plans
- `enforce_policy()` - Adjust tax rates dynamically

### 7. Crime & Legal System (`crime.py`)

**Pipeline:**
Crime Detected → Investigation (50% resolve) → Trial → Sentencing → Prison

**Crime Detection:**
- Negative balance (desperation)
- Business owners (fraud risk)
- Low-skill construction workers (safety violations)

**Sentence Calculation:**
- Severity level (1-5) × 24 hours
- Example: Severity 3 = 72 hours prison

### 8. Mining System (`mining.py`)

**Features:**
- Mining companies with employee rosters
- Resource extraction from mines
- Yield rates determined by worker count and skill
- 6 resource types with independent economies

**Key Methods:**
- `discover_mine()` - Add mine to city
- `mine_resources()` - Extract and track output
- `register_company()` - Create mining operation

### 9. Construction System (`construction.py`)

**Project Lifecycle:**
1. Project created with cost, skill requirement, worker slots
2. Workers assigned, progress advances at 15% per worker per tick
3. Completion triggers building creation
4. Workers gain +2 building skill

**Key Methods:**
- `create_project()` - Start construction
- `assign_workers()` - Add workers to project
- `run_projects()` - Advance all projects
- `repair_structure()` - Fix damaged buildings

### 10. Interaction System (`interaction.py`)

**Interaction Types:**
- Conversation (60% create new friendship)
- Trade (balance transfer if funds available)
- Relationship strengthening

**Key Methods:**
- `process_conversation()` - Social bonding
- `process_trade()` - Economic exchange
- `strengthen_relationships()` - Relationship growth over time

### 11. Exploration System (`exploration.py`)

**Discovery Types:**
- Mines (resource deposits)
- Fertile land (farming)
- Water sources
- Resource deposits

**Process:**
1. Explorers with driving skill > 30 explore
2. 30% chance to discover something
3. Skills improve, memories recorded
4. Discovery database updated

### 12. War & Diplomacy (`war.py`)

**Features:**
- Inter-city conflicts
- Alliance system
- Territory reassignment
- Intensity levels (1-5)

**Key Methods:**
- `declare_conflict()` - Start war
- `resolve_conflicts()` - 20% weekly chance to resolve
- `_adjust_territory()` - Territory changes to winner

### 13. Minecraft Connector (`minecraft_connector.py`)

**Stub Implementation** (bridge to actual Minecraft):
- `connect()` - Establish RPC connection
- `load_world_data()` - Import existing structures
- `detect_player()` - Identify active player
- `spawn_citizen_npc()` - Add NPC to world
- `send_citizen_action()` - Execute action in Minecraft
- `broadcast_event()` - Show events to players

**Expected Integration:**
- Paper plugin with socket API
- Fabric mod with RPC endpoint
- Custom protocol for state sync

### 14. Save System (`save_system.py`)

**Database Tables:**
- `citizens` - All 5,000 citizen records
- `cities` - 20 city records
- `buildings` - Town structures
- `roads` - Transportation networks
- `mines` - Resource deposits

**Operations:**
- `save_citizens()` - Persist all agents
- `load_citizens()` - Restore from DB
- `save_world()` - Infrastructure snapshot
- `load_world()` - Restore infrastructure

### 15. Utility Functions (`utils.py`)

**Available Helpers:**
- `get_population_stats()` - Demographics
- `get_city_stats()` - Urban metrics
- `find_citizen_by_name()` - Citizen lookup
- `find_citizens_by_job()` - Job filtering
- `calculate_city_wealth()` - Total balance
- `get_highest_skill_citizens()` - Ranking
- `print_citizen_info()` - Formatted output

## Simulation Tick Flow

```
Tick Execution (every ~500ms):
1. Government Phase
   - Enforce policy
   - Adjust tax rates

2. Economy Phase
   - Update market prices
   - Run business operations
   - Pay salaries
   - Collect taxes

3. Mining Phase
   - Extract resources
   - Update known resources
   - Update market supply

4. Crime Phase
   - Detect crimes
   - Investigate cases
   - Adjudicate (trial)
   - Release prisoners

5. Diplomacy Phase
   - Resolve conflicts
   - Balance alliances

6. Construction Phase
   - Advance projects
   - Discover damaged buildings
   - Repair structures

7. Interaction Phase
   - Social interactions (conversations, trades)
   - Strengthen relationships

8. Active AI Phase
   - Select 250 active citizens
   - Run decision cycles
   - Update memories and skills

9. Background AI Phase
   - Stochastic updates for idle citizens
   - Routine memory checks

10. Save Phase
    - Persist all changes to SQLite
```

## Performance Optimization

**Active vs Background Simulation:**
- **Active** (250 citizens): Full decision cycle, LLM inference
- **Background** (4,750 citizens): Stochastic updates, no inference

**Memory Usage:**
- 5,000 citizens × 5KB average = 25MB
- SQLite database ≈ 50MB
- Runtime structures ≈ 100MB
- **Total: ~200MB base + model weights**

**CPU Usage:**
- 1 tick = ~100-200ms on 4-core CPU
- 250 active citizens × 0.5ms = 125ms
- Background simulation + I/O = 75ms
- **Result: ~2 ticks/second = 120 game-seconds/minute**

## State Persistence

**On Player Disconnect:**
1. Save all citizens and memories
2. Save world infrastructure
3. Clear active flags
4. Close database connection

**On Player Reconnect:**
1. Load civilization state
2. Detect new player location
3. Resume simulation
4. Restore active citizen focus

## Extension Points

### Adding New Subsystems

1. Create new module in `src/engine/`
2. Define dataclass for state
3. Implement core methods
4. Add to `SimulationEngine.__init__()`
5. Wire into `run_tick()` method
6. Add save/load support if needed

### Adding New Citizen Jobs

1. Add job type to job generation in `Citizen.generate_identity()`
2. Implement job-specific behavior in `AIManager._adult_decision()`
3. Add salary and skill requirements

### Adding New Resources

1. Add to `World.resources` default dict
2. Update `Market.prices`, `supply`, `demand`
3. Create mines that produce resource
4. Add extraction logic to `Mining.mine_resources()`

## Testing

```python
# Quick test
from src.engine.gameloop import GameLoop
loop = GameLoop()
loop.run_for_ticks(10)

# Programmatic test
from src.engine.simulation import SimulationEngine
engine = SimulationEngine()
engine.bootstrap()
assert len(engine.citizens) == 5000
assert len(engine.world.cities) == 20
```

## Known Limitations

1. No LLM integration yet (stubs in place)
2. Minecraft connector is mock implementation
3. No UI/dashboard
4. Scaling tested up to 10,000 citizens
5. No multiplayer support yet

## Future Roadmap

- [ ] Real LLM inference for adult/child models
- [ ] Minecraft plugin/mod integration
- [ ] Web dashboard for monitoring
- [ ] Agriculture and farming
- [ ] Transportation and vehicles
- [ ] Cultural factions
- [ ] Natural disasters
- [ ] Mod support
