#!/usr/bin/env python3
"""Seed the Minecraft plugin bridge with all citizens from the simulation engine.

Usage:
  python scripts/seed_population.py --world-path "D:\Minecraft Worlds\saves\city1mansion ai" --batch 500

This script bootstraps the engine, starts the local plugin server (for live interaction),
and registers entities via the `MinecraftPluginHook`. It writes spawn/command lines to
the `<world>/minecraftia` folder.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Optional

from src.engine import SimulationEngine
from src.minecraft.plugin_hook import MinecraftPluginHook
from src.minecraft.plugin_server import MinecraftPluginServer


logger = logging.getLogger("seed_population")


def seed(world_path: str, batch: int = 500, pause: float = 0.25) -> None:
    world = Path(world_path)
    world.mkdir(parents=True, exist_ok=True)

    engine = SimulationEngine()
    logger.info("Bootstrapping simulation engine...")
    engine.bootstrap()

    hook = MinecraftPluginHook(world_path=str(world))
    server = MinecraftPluginServer(world_path=str(world))
    server.start()

    total = len(engine.citizens)
    logger.info("Registering %d citizens in batches of %d...", total, batch)

    try:
        for i in range(0, total, batch):
            subset = engine.citizens[i : i + batch]
            for c in subset:
                entity_id = f"entity_{c.name.replace(' ', '_').lower()}"
                hook.register_entity(entity_id, c.name, c.job.title, c.city)
            # allow a short pause so any file watchers can catch up
            logger.info("Seeded %d/%d citizens", min(i + batch, total), total)
            time.sleep(pause)

        logger.info("Seeding complete: %d citizens registered.", total)
        logger.info("Plugin files written to: %s", str(world / "minecraftia"))

    finally:
        logger.info("Stopping plugin server")
        try:
            server.stop()
        except Exception:
            logger.exception("Error stopping server")


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--world-path", required=False, help="Minecraft world save folder path")
    parser.add_argument("--batch", type=int, default=500, help="Batch size for seeding (default 500)")
    parser.add_argument("--pause", type=float, default=0.25, help="Pause between batches (seconds)")
    args = parser.parse_args(argv)

    world_path = args.world_path or (
        str(Path.cwd() / "minecraft_world")
    )

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    seed(world_path, batch=args.batch, pause=args.pause)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
