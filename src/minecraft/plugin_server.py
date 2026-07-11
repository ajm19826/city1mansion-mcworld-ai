from __future__ import annotations

import json
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Optional

from src.minecraft.plugin_hook import MinecraftPluginHook


class PluginRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        if path == "/state":
            self._send_json(200, self.server.hook.snapshot())
            return
        if path == "/entities":
            self._send_json(200, self.server.hook.get_entities())
            return
        if path.startswith("/entities/"):
            entity_id = path.split("/", 2)[2]
            entity = self.server.hook.get_entity(entity_id)
            if entity is None:
                self._send_json(404, {"error": "entity_not_found"})
                return
            self._send_json(200, entity)
            return
        if path == "/queue":
            self._send_json(200, self.server.hook.get_queue())
            return
        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length).decode("utf-8") if length else "{}"
        data = json.loads(payload) if payload else {}
        path = urllib.parse.urlparse(self.path).path
        if path == "/action":
            entity_id = data.get("entity_id", "unknown")
            action_type = data.get("action_type", "noop")
            payload_data = data.get("payload", {})
            self.server.hook.queue_action(entity_id, action_type, payload_data)
            self.server.hook.process_tick()
            self._send_json(200, {"status": "queued", "entity_id": entity_id, "action_type": action_type})
            return
        if path == "/interact":
            entity_id = data.get("entity_id", "unknown")
            interaction = data.get("interaction", "talk")
            metadata = data.get("metadata", {})
            self.server.hook.queue_interaction(entity_id, interaction, metadata)
            self.server.hook.process_tick()
            self._send_json(200, {"status": "interaction_queued", "entity_id": entity_id, "interaction": interaction})
            return
        if path == "/tick":
            tick = data.get("tick")
            processed = self.server.hook.process_tick(tick=tick)
            self._send_json(200, {"processed": processed})
            return
        self._send_json(404, {"error": "not_found"})

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
            self.server = None
            self.thread = None
