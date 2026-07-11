from __future__ import annotations

import time
from typing import Optional

from src.engine.simulation import SimulationEngine
from src.engine.minecraft_connector import MinecraftConnector


class GameLoop:
    """
    Main game loop for the Minecraftia Civilization Simulator.
    
    Responsibilities:
    - Load/bootstrap the civilization
    - Sync with Minecraft world
    - Run simulation ticks at fixed intervals
    - Save game state
    - Handle player input/detection
    """

    def __init__(self, tick_rate: float = 0.5) -> None:
        self.engine = SimulationEngine()
        self.connector = MinecraftConnector()
        self.tick_rate = tick_rate  # seconds per tick
        self.running = False
        self.tick_count = 0

    def bootstrap(self) -> bool:
        """Initialize and load the civilization."""
        print("[BOOTSTRAP] Loading civilization simulator...")
        self.engine.bootstrap(resume=True)
        print(f"[BOOTSTRAP] Loaded {len(self.engine.citizens)} citizens across {len(self.engine.world.cities)} cities")

        print("[BOOTSTRAP] Attempting Minecraft connection...")
        if self.connector.connect():
            print("[BOOTSTRAP] Connected to Minecraft server")
            world_data = self.connector.load_world_data()
            print(f"[BOOTSTRAP] Loaded world data: {len(world_data.get('buildings', []))} buildings, {len(world_data.get('roads', []))} roads")
        else:
            print("[BOOTSTRAP] Minecraft server not available (will run offline)")

        return True

    def detect_player(self) -> Optional[str]:
        """Detect if a player is in the world."""
        if not self.connector.is_connected:
            return None
        player_name = self.connector.detect_player()
        if player_name and player_name != self.engine.player_location:
            self.engine.player_location = player_name
            print(f"[DETECTION] Player detected: {player_name}")
        return player_name

    def run_tick(self) -> None:
        """Execute one simulation tick."""
        self.tick_count += 1
        self.engine.run_tick()
        if self.tick_count % 10 == 0:
            print(f"[TICK] Simulation tick {self.tick_count} completed")

    def run(self) -> None:
        """Main game loop (blocks until stopped)."""
        if not self.bootstrap():
            print("[ERROR] Failed to bootstrap simulator")
            return

        self.running = True
        print("[GAMELOOP] Starting main loop...")
        try:
            while self.running:
                self.detect_player()
                self.run_tick()
                time.sleep(self.tick_rate)
        except KeyboardInterrupt:
            print("[GAMELOOP] Received interrupt signal")
        finally:
            self.shutdown()

    def run_for_ticks(self, count: int) -> None:
        """Run the simulator for a specified number of ticks."""
        if not self.bootstrap():
            print("[ERROR] Failed to bootstrap simulator")
            return

        print(f"[GAMELOOP] Running for {count} ticks...")
        try:
            for _ in range(count):
                self.detect_player()
                self.run_tick()
                time.sleep(self.tick_rate)
        except KeyboardInterrupt:
            print("[GAMELOOP] Received interrupt signal")
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Gracefully shut down the simulator."""
        print("[SHUTDOWN] Saving civilization state...")
        self.engine.save_state()
        print("[SHUTDOWN] Disconnecting from Minecraft...")
        self.connector.disconnect()
        self.engine.shutdown()
        print("[SHUTDOWN] Civilization simulator halted")
        self.running = False
