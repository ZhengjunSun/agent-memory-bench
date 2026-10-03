import json

from .benchmark import BenchmarkCase, evaluate
from .memory import MemoryStore


def main() -> None:
    store = MemoryStore()
    old = store.add("Lin", "preferred_model", "Model-A", valid_from=1)
    store.add("Lin", "preferred_model", "Model-B", valid_from=2, supersedes=old.memory_id)
    store.add("Plant-7", "maintenance_window", "Sunday 02:00", valid_from=1)
    cases = [
        BenchmarkCase("current", "Lin preferred model", frozenset({"Model-B"})),
        BenchmarkCase("historical", "Lin preferred model", frozenset({"Model-A"}), as_of=1),
        BenchmarkCase("schedule", "Plant-7 maintenance", frozenset({"Sunday 02:00"})),
        BenchmarkCase("unknown", "Who owns Site-Z?", frozenset(), should_abstain=True),
    ]
    print(json.dumps(evaluate(store, cases), indent=2))


if __name__ == "__main__":
    main()
