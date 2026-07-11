import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.production import ProductionCivilizationRuntime, PerformanceConfig


def parse_bool_env(name: str) -> bool:
    value = os.environ.get(name, "")
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Minecraftia AI Civilization Simulator")
    parser.add_argument(
        "--world-path",
        default=os.environ.get("MINECRAFT_WORLD_PATH", r"D:\Minecraft Worlds\saves\city1mansion ai"),
        help="Minecraft world save folder path",
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=int(os.environ.get("SIM_TICKS", "0")),
        help="Number of simulation ticks to run (0 for indefinite)",
    )
    parser.add_argument(
        "--max-agents-per-tick",
        type=int,
        default=int(os.environ.get("MAX_AGENTS_PER_TICK", "40")),
        help="Maximum number of agents to process per tick",
    )
    parser.add_argument(
        "--max-active-citizens",
        type=int,
        default=int(os.environ.get("MAX_ACTIVE_CITIZENS", "80")),
        help="Maximum number of active citizens in the simulation",
    )
    parser.add_argument(
        "--tick-interval-seconds",
        type=float,
        default=float(os.environ.get("TICK_INTERVAL_SECONDS", "1.0")),
        help="Seconds between each simulation tick",
    )
    parser.add_argument(
        "--enable-online-model",
        action="store_true",
        default=parse_bool_env("ENABLE_ONLINE_MODEL"),
        help="Enable the AI online model call path",
    )
    parser.add_argument(
        "--plugin-api-key",
        default=os.environ.get("PLUGIN_API_KEY"),
        help="Simple API key for HTTP bridge mutating endpoints",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print("Starting Minecraftia AI Civilization Simulator for a private Minecraft world...")
    world_path = args.world_path
    config = PerformanceConfig(
        max_agents_per_tick=args.max_agents_per_tick,
        max_active_citizens=args.max_active_citizens,
        tick_interval_seconds=args.tick_interval_seconds,
    )
    runtime = ProductionCivilizationRuntime(config=config, world_path=world_path)
    runtime.sim.minecraft.mode = "private_world"
    runtime.sim.decision_engine.model_enabled = args.enable_online_model
    if args.plugin_api_key:
        os.environ["PLUGIN_API_KEY"] = args.plugin_api_key
        print("Plugin API key mode enabled.")
    if args.enable_online_model:
        print("Online AI model path enabled.")
    print("Plugin server running at http://127.0.0.1:8765")
    print("Press CTRL+C to stop the simulator.")
    try:
        runtime.run(ticks=args.ticks if args.ticks > 0 else None)
    except KeyboardInterrupt:
        print("Stopping simulation...")
    finally:
        runtime.stop()
        print(f"Simulation stopped. Actions written to {world_path}")


if __name__ == "__main__":
    main()
