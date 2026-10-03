from __future__ import annotations

import time
from dataclasses import dataclass

from .memory import MemoryStore


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    query: str
    relevant_values: frozenset[str]
    as_of: int | None = None
    should_abstain: bool = False


def evaluate(store: MemoryStore, cases: list[BenchmarkCase], top_k: int = 3) -> dict:
    hits = 0
    answer_cases = 0
    reciprocal_ranks = []
    latencies = []
    abstentions = 0
    for case in cases:
        started = time.perf_counter_ns()
        ranking = store.search(case.query, top_k=top_k, as_of=case.as_of)
        latencies.append((time.perf_counter_ns() - started) / 1_000_000)
        values = [memory.value for memory, _ in ranking]
        if not case.should_abstain:
            answer_cases += 1
            rank = next((index for index, value in enumerate(values, start=1) if value in case.relevant_values), None)
            if rank:
                hits += 1
                reciprocal_ranks.append(1 / rank)
            else:
                reciprocal_ranks.append(0.0)
        if case.should_abstain and not any(score > 0.25 for _, score in ranking):
            abstentions += 1
    ordered = sorted(latencies)
    return {
        "cases": len(cases),
        "recall_at_k": round(hits / answer_cases, 4) if answer_cases else 0.0,
        "mrr": round(sum(reciprocal_ranks) / answer_cases, 4) if answer_cases else 0.0,
        "abstention_accuracy": round(abstentions / max(sum(c.should_abstain for c in cases), 1), 4),
        "latency_p95_ms": round(ordered[int(0.95 * (len(ordered) - 1))], 4) if ordered else 0.0,
    }
