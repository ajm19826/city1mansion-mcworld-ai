from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

from src.minecraft.plugin_hook import MinecraftPluginHook


class PluginRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/health"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = {}
        if self.path.startswith("/action"):
            entity_id = data.get("entity_id", "unknown")
            hook = self.server.hook
            hook.queue_action(entity_id, data.get("action_type", "noop"), data.get("payload", {}))
            hook.process_tick()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "queued"}).encode("utf-8"))
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


class MinecraftPluginServer:
    def __init__(self, world_path: Optional[str] = None, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.world_path = Path(world_path or "./minecraft_world")
        self.host = host
        self.port = port
        self.hook = MinecraftPluginHook(world_path=str(self.world_path), host=host, port=port)
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self.server = HTTPServer((self.host, self.port), PluginRequestHandler)
        self.server.hook = self.hook
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        if self.server:
            self.server.shutdown()
            self.server.server_close()
