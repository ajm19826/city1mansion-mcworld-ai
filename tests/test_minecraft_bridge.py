from pathlib import Path

from src.minecraft.bridge import MinecraftBridge


def test_bridge_persists_command_stream_and_mcfunction(tmp_path: Path):
    bridge = MinecraftBridge(world_path=str(tmp_path))
    bridge.emit_build_command("Agent_1", "Monesttery")
    bridge.emit_explore_command("Agent_2", "Sand Yusef")

    state_path = tmp_path / "minecraftia" / "bridge_state.json"
    commands_path = tmp_path / "minecraftia" / "commands.jsonl"
    mcfunction_path = tmp_path / "minecraftia" / "minecraftia_bridge.mcfunction"

    assert state_path.exists()
    assert commands_path.exists()
    assert mcfunction_path.exists()
    assert len(bridge.load_commands()) == 2
