from __future__ import annotations

import argparse
import json

from agent_memory_bench.benchmark import BenchmarkCase, evaluate
from agent_memory_bench.memory import MemoryStore


def run(facts: int, queries: int) -> dict:
    store = MemoryStore()
    cases = []
    for index in range(facts):
        store.add(f"asset-{index}", "owner", f"team-{index % 17}", valid_from=1)
    for index in range(queries):
        if index % 10 == 0:
            cases.append(
                BenchmarkCase(
                    f"q-{index}",
                    "lunar outpost steward",
                    frozenset(),
                    should_abstain=True,
                )
            )
            continue
        asset = index % facts
        cases.append(
            BenchmarkCase(
                f"q-{index}",
                f"asset-{asset} owner",
                frozenset({f"team-{asset % 17}"}),
            )
        )
    result = evaluate(store, cases)
    return {"facts": facts, "queries": queries, **result}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--facts", type=int, default=1000)
    parser.add_argument("--queries", type=int, default=200)
    args = parser.parse_args()
    print(json.dumps(run(args.facts, args.queries), indent=2))


if __name__ == "__main__":
    main()
