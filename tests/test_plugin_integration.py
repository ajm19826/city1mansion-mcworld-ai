import json
import os
import tempfile
import time
import urllib.request
import urllib.error

from src.minecraft.plugin_server import MinecraftPluginServer


def test_plugin_server_integration():
    temp_dir = tempfile.mkdtemp(prefix="mcint_")
    try:
        # set API key
        os.environ["PLUGIN_API_KEY"] = "testkey123"
        server = MinecraftPluginServer(world_path=temp_dir, host="127.0.0.1", port=0)
        # prefer explicit api_key from env
        server.api_key = os.environ.get("PLUGIN_API_KEY")
        server.start()
        # wait for server to start
        time.sleep(0.1)
        assert server.server is not None
        port = server.server.server_address[1]

        # health check (no api key required)
        resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/health")
        assert resp.status == 200

        # queue action (requires API key)
        data = json.dumps({"entity_id": "entity_alice", "action_type": "build", "payload": {"location": "Monesttery"}}).encode("utf-8")
        req = urllib.request.Request(f"http://127.0.0.1:{port}/action", data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Api-Key", os.environ.get("PLUGIN_API_KEY"))
        resp = urllib.request.urlopen(req)
        body = json.loads(resp.read().decode("utf-8"))
        assert resp.status == 200
        assert body.get("status") == "queued"

    finally:
        try:
            server.stop()
        except Exception:
            pass