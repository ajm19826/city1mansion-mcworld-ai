from __future__ import annotations

import json
import logging
import re
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Optional

from src.minecraft.plugin_hook import MinecraftPluginHook


logger = logging.getLogger(__name__)


def _safe_entity_id(value: str) -> Optional[str]:
    if not value:
        return None
    # allow alphanumeric, underscore, hyphen
    if re.match(r"^[A-Za-z0-9_\-]+$", value):
        return value
    return None


class PluginRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: Any) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _bad_request(self, message: str) -> None:
        self._send_json(400, {"error": "bad_request", "message": message})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        logger.debug("GET %s", path)
        if path == "/health":
            # basic health: check writeable plugin folder
            try:
                state_dir = self.server.hook.state_path.parent
                state_dir.mkdir(parents=True, exist_ok=True)
                test_file = state_dir / ".health_check.tmp"
                with test_file.open("w", encoding="utf-8") as fh:
                    fh.write("ok")
                try:
                    test_file.unlink()
                except Exception:
                    pass
                self._send_json(200, {"status": "ok"})
            except Exception as exc:
                logger.exception("Health check failed: %s", exc)
                self._send_json(500, {"status": "error", "message": str(exc)})
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
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(payload) if payload else {}
        except Exception:
            return self._bad_request("invalid_json")
        logger.debug("POST %s payload=%s", path, data)

        # simple API key auth for mutating endpoints
        expected_key = getattr(self.server, "api_key", None)
        if path in ("/action", "/interact", "/tick") and expected_key:
            provided = self.headers.get("X-Api-Key") or self.headers.get("X-API-KEY")
            if provided != expected_key:
                logger.warning("Unauthorized request for %s from %s", path, self.client_address)
                self._send_json(401, {"error": "unauthorized"})
                return
        if path == "/action":
            entity_id = data.get("entity_id")
            safe_id = _safe_entity_id(entity_id)
            if not safe_id:
                return self._bad_request("invalid_entity_id")
            action_type = data.get("action_type", "noop")
            allowed = {"build", "explore", "govern", "economy", "interact", "noop"}
            if action_type not in allowed:
                return self._bad_request("invalid_action_type")
            payload_data = data.get("payload", {}) or {}
            self.server.hook.queue_action(safe_id, action_type, payload_data)
            self.server.hook.process_tick()
            logger.info("Queued action %s for %s", action_type, safe_id)
            self._send_json(200, {"status": "queued", "entity_id": safe_id, "action_type": action_type})
            return
        if path == "/interact":
            entity_id = data.get("entity_id")
            safe_id = _safe_entity_id(entity_id)
            if not safe_id:
                return self._bad_request("invalid_entity_id")
            interaction = data.get("interaction", "talk")
            metadata = data.get("metadata", {}) or {}
            self.server.hook.queue_interaction(safe_id, interaction, metadata)
            self.server.hook.process_tick()
            logger.info("Queued interaction %s for %s", interaction, safe_id)
            self._send_json(200, {"status": "interaction_queued", "entity_id": safe_id, "interaction": interaction})
            return
        if path == "/tick":
            tick = data.get("tick")
            try:
                processed = self.server.hook.process_tick(tick=tick)
            except Exception as exc:
                logger.exception("Tick processing failed: %s", exc)
                return self._send_json(500, {"error": "tick_failed", "message": str(exc)})
            self._send_json(200, {"processed": processed})
            return
        self._send_json(404, {"error": "not_found"})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        # silence BaseHTTPRequestHandler default logging; use structured logger instead
        logger.debug(format % args)


class MinecraftPluginServer:
    def __init__(self, world_path: Optional[str] = None, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.world_path = Path(world_path or "./minecraft_world")
        self.host = host
        self.port = port
        self.hook = MinecraftPluginHook(world_path=str(self.world_path), host=host, port=port)
        # API key may be provided via environment variable PLUGIN_API_KEY
        import os
        self.api_key = os.environ.get("PLUGIN_API_KEY")
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self.server is not None:
            return
        try:
            self.server = HTTPServer((self.host, self.port), PluginRequestHandler)
            self.server.hook = self.hook
            # attach api_key to server so handlers can access it
            self.server.api_key = self.api_key
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            logger.info("MinecraftPluginServer started on %s:%s", self.host, self.port)
        except Exception as exc:  # pragma: no cover - best-effort in prod
            logger.exception("Failed to start plugin server: %s", exc)

    def stop(self) -> None:
        if self.server:
            try:
                logger.info("Stopping MinecraftPluginServer on %s:%s", self.host, self.port)
                self.server.shutdown()
                self.server.server_close()
                if self.thread and self.thread.is_alive():
                    self.thread.join(timeout=2.0)
            except Exception:
                logger.exception("Error while stopping server")
            finally:
                self.server = None
                self.thread = None
