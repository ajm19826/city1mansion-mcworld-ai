from pathlib import Path

from src.minecraft.integration import MinecraftIntegration


def test_private_world_integration_writes_local_actions(tmp_path: Path):
    world_path = tmp_path / "private_world"
    integration = MinecraftIntegration(enabled=True, mode="private_world", world_path=str(world_path))
    assert integration.connect() is True

    action = integration.execute_decision({"action": "assign_workers"}, "Agent_1")
    assert action is not None
    integration.publish_action(action)

    manifest = world_path / "minecraftia" / "actions.jsonl"
    assert manifest.exists()
    assert "build" in manifest.read_text(encoding="utf-8")
