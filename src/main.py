import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.production import ProductionCivilizationRuntime, PerformanceConfig


def main() -> None:
    print("Starting Minecraftia AI Civilization Simulator for a private Minecraft world...")
    world_path = os.environ.get("MINECRAFT_WORLD_PATH", r"D:\Minecraft Worlds\saves\city1mansion ai")
    config = PerformanceConfig(max_agents_per_tick=40, max_active_citizens=80, tick_interval_seconds=1.0)
    runtime = ProductionCivilizationRuntime(config=config)
    runtime.sim.minecraft.mode = "private_world"
    runtime.sim.minecraft.world_path = world_path
    runtime.run(ticks=5)
    print(f"Private-world AI simulation cycle completed. Actions written to {world_path}")


if __name__ == "__main__":
    main()
