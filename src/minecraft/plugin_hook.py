from __future__ import annotations

import json
import logging
import os
import tempfile
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class MinecraftPluginHook:
    """Production-grade bridge for a Minecraft mod/plugin runtime.

    The hook persists entity state, action queues, and command exports under the
    target Minecraft save folder so the AI population can resume across restarts.
    """

    def __init__(self, world_path: Optional[str] = None, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.world_path = Path(world_path or "./minecraft_world")
        self.host = host
        self.port = port
        self.state_path = self.world_path / "minecraftia" / "plugin_state.json"
        self.queue_path = self.world_path / "minecraftia" / "plugin_queue.jsonl"
        self.entities_path = self.world_path / "minecraftia" / "live_entities.json"
        self.commands_path = self.world_path / "minecraftia" / "plugin_commands.mcfunction"
        self.interactions_path = self.world_path / "minecraftia" / "plugin_interactions.jsonl"
        self.state: Dict[str, Any] = {"tick": 0, "entities": {}, "actions": []}
        self.lock = threading.Lock()
        self.datapack_path = self.world_path / "datapacks" / "minecraftia_bridge"
        self.datapack_data_path = self.datapack_path / "data" / "minecraftia" / "functions"
        self.datapack_pack_path = self.datapack_path / "pack.mcmeta"
        self.datapack_spawn_path = self.datapack_data_path / "spawn_entities.mcfunction"
        self.datapack_load_path = self.datapack_data_path / "load.mcfunction"
        self.datapack_load_tag_path = self.datapack_path / "data" / "minecraft" / "tags" / "functions" / "load.json"
        self.datapack_tick_path = self.datapack_data_path / "tick.mcfunction"
        self._load_state()
        self._ensure_files()

    def _ensure_files(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)
        self.entities_path.parent.mkdir(parents=True, exist_ok=True)
        self.commands_path.parent.mkdir(parents=True, exist_ok=True)
        self.interactions_path.parent.mkdir(parents=True, exist_ok=True)
        self.datapack_spawn_path.parent.mkdir(parents=True, exist_ok=True)
        self.datapack_load_path.parent.mkdir(parents=True, exist_ok=True)
        self.datapack_load_tag_path.parent.mkdir(parents=True, exist_ok=True)
        self.datapack_pack_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> None:
        self._ensure_files()
        if self.state_path.exists():
            with self.state_path.open("r", encoding="utf-8") as handle:
                self.state = json.load(handle)
        self.state.setdefault("tick", 0)
        self.state.setdefault("entities", {})
        self.state.setdefault("actions", [])
        self._ensure_datapack()

    def _ensure_datapack(self) -> None:
        self.datapack_path.mkdir(parents=True, exist_ok=True)
        self.datapack_data_path.mkdir(parents=True, exist_ok=True)
        self.datapack_load_path.parent.mkdir(parents=True, exist_ok=True)
        self.datapack_load_tag_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.datapack_pack_path.exists():
            self.datapack_pack_path.write_text(
                json.dumps({"pack": {"pack_format": 15, "description": "Minecraftia bridge datapack"}}, indent=2),
                encoding="utf-8",
            )
        if not self.datapack_load_path.exists():
            self.datapack_load_path.write_text("# Minecraftia bridge load function\nfunction minecraftia:spawn_entities\n", encoding="utf-8")
        if not self.datapack_tick_path.exists():
            self.datapack_tick_path.write_text("# Minecraftia bridge tick function\n", encoding="utf-8")
        if not self.datapack_spawn_path.exists():
            self.datapack_spawn_path.write_text("# Minecraftia bridge spawn function\n", encoding="utf-8")
        if not self.datapack_load_tag_path.exists():
            self.datapack_load_tag_path.write_text(
                json.dumps({"values": ["minecraftia:load"]}, indent=2),
                encoding="utf-8",
            )

    def _ensure_datapack(self) -> None:
        self.datapack_path.mkdir(parents=True, exist_ok=True)
        self.datapack_data_path.mkdir(parents=True, exist_ok=True)
        if not self.datapack_pack_path.exists():
            self.datapack_pack_path.write_text(
                json.dumps({"pack": {"pack_format": 15, "description": "Minecraftia bridge datapack"}}, indent=2),
                encoding="utf-8",
            )
        if not self.datapack_load_path.exists():
            self.datapack_load_path.write_text("# Minecraftia bridge load function\n", encoding="utf-8")
        if not self.datapack_tick_path.exists():
            self.datapack_tick_path.write_text("# Minecraftia bridge tick function\n", encoding="utf-8")
        if not self.datapack_spawn_path.exists():
            self.datapack_spawn_path.write_text("# Minecraftia bridge spawn function\n", encoding="utf-8")

    def _save_state(self) -> None:
        with self.lock:
            try:
                self._ensure_files()
                # atomic write to avoid partial/corrupt state files
                tmp_fd, tmp_path = tempfile.mkstemp(dir=str(self.state_path.parent), prefix=".state_tmp_")
                try:
                    with os.fdopen(tmp_fd, "w", encoding="utf-8") as handle:
                        json.dump(self.state, handle, indent=2, sort_keys=True)
                        handle.flush()
                        os.fsync(handle.fileno())
                    os.replace(tmp_path, str(self.state_path))
                finally:
                    if os.path.exists(tmp_path):
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Failed to save plugin state: %s", exc)

    def persist_state(self) -> None:
        self._save_state()

    def register_entity(
        self,
        entity_id: str,
        name: str,
        role: str,
        location: str,
        position: Optional[Dict[str, float]] = None,
        save: bool = True,
    ) -> Dict[str, Any]:
        with self.lock:
            self._ensure_files()
            entities = self.state.setdefault("entities", {})
            entity = entities.get(entity_id)
            if entity is None:
                entity = {
                    "entity_id": entity_id,
                    "name": name,
                    "role": role,
                    "location": location,
                    "position": position or {"x": 0.0, "y": 64.0, "z": 0.0},
                    "thinking": True,
                    "health": 20,
                    "inventory": [],
                    "last_action": None,
                    "spawned": False,
                }
                entities[entity_id] = entity
                self._write_spawn_command(entity)
            else:
                entity["name"] = name
                entity["role"] = role
                entity["location"] = location
                entity["position"] = position or entity.get("position", {"x": 0.0, "y": 64.0, "z": 0.0})
                entity["thinking"] = True
            if save:
                self._save_state()
            return entity

    def get_entities(self) -> Dict[str, Any]:
        return self.state.get("entities", {})

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        return self.state.setdefault("entities", {}).get(entity_id)

    def get_queue(self) -> List[Dict[str, Any]]:
        return list(self.state.get("actions", []))

    def queue_action(self, entity_id: str, action_type: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        with self.lock:
            self._ensure_files()
            action = {
                "entity_id": entity_id,
                "action_type": action_type,
                "payload": payload or {},
                "tick": int(self.state.get("tick", 0)),
            }
            self.state.setdefault("actions", []).append(action)
            self._append_queue(action)
            self._save_state()
            return action

    def queue_interaction(self, entity_id: str, interaction: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"interaction": interaction, **(metadata or {})}
        action = self.queue_action(entity_id, "interact", payload)
        self._write_interaction_command(entity_id, interaction, payload)
        return action

    def process_tick(self, tick: Optional[int] = None) -> List[Dict[str, Any]]:
        with self.lock:
            self._ensure_files()
            self.state["tick"] = int(tick if tick is not None else self.state.get("tick", 0) + 1)
            actions = list(self.state.get("actions", []))
            processed: List[Dict[str, Any]] = []
            for action in actions:
                entity_id = action.get("entity_id")
                entity = self.state.setdefault("entities", {}).get(entity_id)
                if not entity:
                    continue
                entity["thinking"] = True
                entity["last_action"] = action
                self._apply_action(entity, action)
                processed.append(action)
            self.state["actions"] = []
            self._save_entities()
            self._save_state()
            return processed

    def _apply_action(self, entity: Dict[str, Any], action: Dict[str, Any]) -> None:
        action_type = action.get("action_type")
        payload = action.get("payload", {})
        if action_type == "build":
            entity["location"] = payload.get("location", entity.get("location"))
            entity.setdefault("inventory", []).append({"item": payload.get("block", "oak_planks")})
            self._write_command(entity, "build", payload)
        elif action_type == "explore":
            entity["location"] = payload.get("location", entity.get("location"))
            self._write_command(entity, "explore", payload)
        elif action_type == "govern":
            self._write_command(entity, "govern", payload)
        elif action_type == "economy":
            entity.setdefault("inventory", []).append({"item": payload.get("item", "emerald"), "count": payload.get("count", 1)})
            self._write_command(entity, "economy", payload)
        elif action_type == "interact":
            self._write_interaction_command(entity, payload.get("interaction", "interact"), payload)
        else:
            self._write_command(entity, "noop", payload)

    def _append_queue(self, action: Dict[str, Any]) -> None:
        with self.queue_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(action) + "\n")

    def _write_spawn_command(self, entity: Dict[str, Any]) -> None:
        spawn_x = entity.get("position", {}).get("x", 0.0)
        spawn_y = entity.get("position", {}).get("y", 64.0)
        spawn_z = entity.get("position", {}).get("z", 0.0)
        with self.commands_path.open("a", encoding="utf-8") as handle:
            handle.write(
                f"# spawn {entity['name']} as {entity['role']} at {entity['location']}\n"
                f"summon villager {spawn_x} {spawn_y} {spawn_z} {{CustomName:'{{\"text\":\"{entity['name']}\"}}', Tags:['minecraftia','ai','{entity['entity_id']}'], CustomNameVisible:1b}}\n"
            )
            entity["spawned"] = True
        self._write_datapack_spawn(entity)

    def _write_datapack_spawn(self, entity: Dict[str, Any]) -> None:
        spawn_x = int(entity.get("position", {}).get("x", 0.0))
        spawn_y = int(entity.get("position", {}).get("y", 64.0))
        spawn_z = int(entity.get("position", {}).get("z", 0.0))
        with self.datapack_spawn_path.open("a", encoding="utf-8") as handle:
            handle.write(
                f"# spawn {entity['name']} as {entity['role']} at {entity['location']}\n"
                f"execute unless entity @e[tag={entity['entity_id']}],sort=nearest,limit=1 run summon villager {spawn_x} {spawn_y} {spawn_z} "
                f"{{CustomName:'{{\"text\":\"{entity['name']}\"}}',Tags:['minecraftia','ai','{entity['entity_id']}'],CustomNameVisible:1b}}\n"
            )

    def _write_command(self, entity: Dict[str, Any], action_type: str, payload: Dict[str, Any]) -> None:
        with self.commands_path.open("a", encoding="utf-8") as handle:
            if action_type == "build":
                handle.write(f"# build {entity['name']} -> {payload.get('block', 'oak_planks')}\n")
            elif action_type == "explore":
                handle.write(f"# explore {entity['name']} -> {payload.get('location', entity['location'])}\n")
            elif action_type == "govern":
                handle.write(f"# govern {entity['name']} -> {payload.get('action', 'govern')}\n")
            elif action_type == "economy":
                handle.write(f"# economy {entity['name']} -> {payload.get('item', 'emerald')}\n")
            else:
                handle.write(f"# noop {entity['name']}\n")

    def _write_interaction_command(self, entity: Dict[str, Any], interaction: str, payload: Dict[str, Any]) -> None:
        with self.interactions_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({
                "entity_id": entity["entity_id"],
                "name": entity["name"],
                "interaction": interaction,
                "payload": payload,
                "tick": int(self.state.get("tick", 0)),
            }) + "\n")
            handle.write(f"# interact {entity['name']} -> {interaction}\n")

    def _save_entities(self) -> None:
        try:
            self._ensure_files()
            tmp_fd, tmp_path = tempfile.mkstemp(dir=str(self.entities_path.parent), prefix=".entities_tmp_")
            try:
                with os.fdopen(tmp_fd, "w", encoding="utf-8") as handle:
                    json.dump(self.state.get("entities", {}), handle, indent=2, sort_keys=True)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(tmp_path, str(self.entities_path))
            finally:
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Failed to save entities file: %s", exc)

    def snapshot(self) -> Dict[str, Any]:
        self._save_entities()
        return {"tick": self.state.get("tick", 0), "entities": self.state.get("entities", {}), "actions": self.state.get("actions", [])}
