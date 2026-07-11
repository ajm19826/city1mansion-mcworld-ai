import logging
import os
import signal
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.production import ProductionCivilizationRuntime, PerformanceConfig

logger = logging.getLogger(__name__)




def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    logger.info("Starting Minecraftia AI Civilization Simulator for a private Minecraft world...")
    world_path = os.environ.get("MINECRAFT_WORLD_PATH", r"D:\Minecraft Worlds\saves\city1mansion ai")
    config = PerformanceConfig(max_agents_per_tick=40, max_active_citizens=80, tick_interval_seconds=1.0)
    runtime = ProductionCivilizationRuntime(config=config, world_path=world_path)
    runtime.sim.minecraft.mode = "private_world"

    ticks_env = os.environ.get("SIM_TICKS")
    ticks = None if ticks_env is None or ticks_env == "" else int(ticks_env)

    # install signal handlers for graceful shutdown
    def _shutdown(signum, frame):
        logger.info("Signal %s received, stopping runtime...", signum)
        try:
            runtime.stop()
        except Exception:
            logger.exception("Error during shutdown")

    signal.signal(signal.SIGINT, _shutdown)
    try:
        signal.signal(signal.SIGTERM, _shutdown)
    except Exception:
        # SIGTERM may not be available on all platforms
        pass

    try:
        if ticks is None or ticks <= 0:
            logger.info("Running indefinitely. Press Ctrl+C to stop the simulator.")
            runtime.run(ticks=None)
        else:
            runtime.run(ticks=ticks)
            logger.info("Private-world AI simulation completed for %s ticks. Actions written to %s", ticks, world_path)
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user.")
    finally:
        runtime.stop()
        logger.info("Runtime stopped and plugin bridge shut down.")


if __name__ == "__main__":
    main()
