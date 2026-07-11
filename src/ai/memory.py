from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class MemoryEntry:
    content: str
    importance: int
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    memory_type: str = "short_term"


class MemorySystem:
    def __init__(self) -> None:
        self.short_term: List[MemoryEntry] = []
        self.long_term: List[MemoryEntry] = []

    def add(self, content: str, importance: int = 1, memory_type: str = "short_term") -> None:
        entry = MemoryEntry(content=content, importance=importance, memory_type=memory_type)
        if memory_type == "long_term":
            self.long_term.append(entry)
            if len(self.long_term) > 50:
                self.long_term = self.long_term[-50:]
        else:
            self.short_term.append(entry)
            if len(self.short_term) > 20:
                self.short_term = self.short_term[-20:]

    def recall(self, limit: int = 5) -> List[MemoryEntry]:
        combined = self.long_term + self.short_term
        combined.sort(key=lambda entry: (entry.importance, entry.timestamp), reverse=True)
        return combined[:limit]
