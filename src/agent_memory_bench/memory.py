from __future__ import annotations

import math
import re
import sqlite3
import time
import uuid
from collections import Counter
from dataclasses import dataclass


def tokenize(text: str) -> list[str]:
    latin = re.findall(r"[a-z0-9_]+", text.lower())
    chinese = [char for char in text if "\u4e00" <= char <= "\u9fff"]
    return latin + chinese


@dataclass(frozen=True)
class Memory:
    memory_id: str
    subject: str
    predicate: str
    value: str
    valid_from: int
    created_at: int
    supersedes: str | None = None

    @property
    def text(self) -> str:
        return f"{self.subject} {self.predicate} {self.value}"


class MemoryStore:
    def __init__(self, database: str = ":memory:") -> None:
        self.db = sqlite3.connect(database)
        self.db.row_factory = sqlite3.Row
        self.db.execute("""
        CREATE TABLE IF NOT EXISTS memories(
          memory_id TEXT PRIMARY KEY, subject TEXT NOT NULL, predicate TEXT NOT NULL,
          value TEXT NOT NULL, valid_from INTEGER NOT NULL, created_at INTEGER NOT NULL,
          supersedes TEXT
        )
        """)

    def add(self, subject: str, predicate: str, value: str, valid_from: int, supersedes: str | None = None) -> Memory:
        if supersedes and not self.get(supersedes):
            raise KeyError(f"unknown superseded memory: {supersedes}")
        memory = Memory(uuid.uuid4().hex, subject, predicate, value, valid_from, time.time_ns(), supersedes)
        self.db.execute("INSERT INTO memories VALUES(?,?,?,?,?,?,?)", tuple(memory.__dict__.values()))
        self.db.commit()
        return memory

    def get(self, memory_id: str) -> Memory | None:
        row = self.db.execute("SELECT * FROM memories WHERE memory_id=?", (memory_id,)).fetchone()
        return Memory(**dict(row)) if row else None

    def all(self) -> list[Memory]:
        return [Memory(**dict(row)) for row in self.db.execute("SELECT * FROM memories")]

    def current(self, subject: str, predicate: str) -> Memory | None:
        candidates = [m for m in self.all() if m.subject == subject and m.predicate == predicate]
        return max(candidates, key=lambda m: (m.valid_from, m.created_at), default=None)

    def search(self, query: str, top_k: int = 5, as_of: int | None = None) -> list[tuple[Memory, float]]:
        memories = [m for m in self.all() if as_of is None or m.valid_from <= as_of]
        if not memories:
            return []
        query_terms = tokenize(query)
        documents = {m.memory_id: Counter(tokenize(m.text)) for m in memories}
        df = Counter(term for counts in documents.values() for term in counts)
        average_length = sum(sum(c.values()) for c in documents.values()) / len(documents)
        latest_time = max(m.valid_from for m in memories)
        scored = []
        for memory in memories:
            counts = documents[memory.memory_id]
            lexical = 0.0
            for term in query_terms:
                frequency = counts[term]
                if frequency:
                    inverse = math.log(1 + (len(memories) - df[term] + 0.5) / (df[term] + 0.5))
                    lexical += inverse * frequency * 2.2 / (frequency + 1.2 * (0.25 + 0.75 * sum(counts.values()) / average_length))
            entity = 1.0 if memory.subject.lower() in query.lower() else 0.0
            recency = 1 / (1 + max(0, latest_time - memory.valid_from))
            scored.append((memory, lexical + 1.5 * entity + 0.2 * recency))
        return sorted(scored, key=lambda item: (-item[1], -item[0].valid_from))[:top_k]

    def context(self, query: str, token_budget: int = 120, as_of: int | None = None) -> list[Memory]:
        selected: list[Memory] = []
        used = 0
        for memory, _ in self.search(query, top_k=20, as_of=as_of):
            estimate = max(1, len(memory.text) // 4)
            if used + estimate > token_budget:
                continue
            selected.append(memory)
            used += estimate
        return selected
