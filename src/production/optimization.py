from __future__ import annotations

import os
import threading
from typing import Any


class ResourceAwareScheduler:
    def __init__(self) -> None:
        self._stop_event = threading.Event()

    def start(self, target: Any, interval_seconds: float = 0.5) -> None:
        def loop() -> None:
            while not self._stop_event.is_set():
                target()
                self._stop_event.wait(interval_seconds)

        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def get_system_load(self) -> Dict[str, float]:
        return {
            "cpu": 0.0,
            "memory_mb": 0.0,
        }
