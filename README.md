# city1mansion-mcworld-ai
The AI Civilization for Minecraft.

## Overview

This project runs a private AI civilization simulation and writes bridge artifacts into a Minecraft world save folder.

The simulator now creates a live plugin bridge under `minecraftia/` inside your world folder:

- `plugin_state.json` — current AI tick, entities, and action queue
- `live_entities.json` — live entity state for NPCs
- `plugin_commands.mcfunction` — exported build/govern/explore/economy commands
- `plugin_queue.jsonl` — queued actions for the bridge
- `plugin_interactions.jsonl` — direct player interaction events

## Production-ready setup

1. Set your Minecraft world folder path using `MINECRAFT_WORLD_PATH`.
2. Run `src/main.py` from the project root.
3. The simulator starts the HTTP bridge at `http://127.0.0.1:8765`.

## Interaction API

Use these endpoints to interact with live AI entities:

- `GET /health` — health check
- `GET /state` — current bridge snapshot
- `GET /entities` — all AI entities
- `GET /entities/{entity_id}` — one entity
- `GET /queue` — pending entity queue
- `POST /action` — queue an action for an entity
- `POST /interact` — send a direct interaction command
- `POST /tick` — advance the bridge tick manually

### Example `curl` commands

```bash
curl http://127.0.0.1:8765/health
curl http://127.0.0.1:8765/state
curl http://127.0.0.1:8765/entities
curl http://127.0.0.1:8765/entities/entity_alice

curl -X POST http://127.0.0.1:8765/action \
  -H 'Content-Type: application/json' \
  -d '{"entity_id":"entity_alice","action_type":"build","payload":{"location":"Monesttery","block":"stone"}}'

curl -X POST http://127.0.0.1:8765/interact \
  -H 'Content-Type: application/json' \
  -d '{"entity_id":"entity_alice","interaction":"trade","metadata":{"offer":"emerald"}}'

curl -X POST http://127.0.0.1:8765/tick \
  -H 'Content-Type: application/json' \
  -d '{}' 
```
