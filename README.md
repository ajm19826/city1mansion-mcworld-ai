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
3. The simulator starts the HTTP bridge at `http://127.0.0.1:8765` and keeps it alive until the runtime stops.

Use `SIM_TICKS=0` or leave `SIM_TICKS` undefined to run indefinitely and keep the bridge available for live interaction.

### Enable online AI mode

Run the simulator with the `--enable-online-model` flag, or set `ENABLE_ONLINE_MODEL=true` in the environment.

```powershell
python -m src.main --world-path "D:\Minecraft Worlds\saves\city1mansion ai" --enable-online-model
```

### One-command startup with seeding

Use this sequence to seed the world and then launch the simulator with online AI enabled:

```powershell
python .\scripts\seed_population.py --world-path "D:\Minecraft Worlds\saves\city1mansion ai" ; python -m src.main --world-path "D:\Minecraft Worlds\saves\city1mansion ai" --enable-online-model
```

For a Windows CMD shell:

```cmd
python scripts\seed_population.py --world-path "D:\Minecraft Worlds\saves\city1mansion ai" && python -m src.main --world-path "D:\Minecraft Worlds\saves\city1mansion ai" --enable-online-model
```

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

Authentication
--------------

For local private use you can optionally enable a simple API key by setting the `PLUGIN_API_KEY` environment variable. When set, mutating endpoints (`/action`, `/interact`, `/tick`) require the header `X-Api-Key: <your-key>`.

Example:

```bash
export PLUGIN_API_KEY="my_secret"
curl -X POST http://127.0.0.1:8765/action \
  -H 'Content-Type: application/json' \
  -H 'X-Api-Key: my_secret' \
  -d '{"entity_id":"entity_alice","action_type":"build","payload":{"location":"Monesttery"}}'
```

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
