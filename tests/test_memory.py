import unittest

from agent_memory_bench import BenchmarkCase, MemoryStore, evaluate


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.store = MemoryStore()
        old = self.store.add("A", "status", "offline", 1)
        self.store.add("A", "status", "online", 2, supersedes=old.memory_id)
        self.store.add("B", "owner", "Chen", 1)

    def test_current_fact_uses_latest_valid_time(self):
        self.assertEqual(self.store.current("A", "status").value, "online")

    def test_as_of_search_excludes_future_fact(self):
        values = [m.value for m, _ in self.store.search("A status", as_of=1)]
        self.assertIn("offline", values)
        self.assertNotIn("online", values)

    def test_context_respects_budget(self):
        context = self.store.context("status owner", token_budget=4)
        self.assertLessEqual(sum(max(1, len(m.text) // 4) for m in context), 4)

    def test_benchmark(self):
        report = evaluate(self.store, [BenchmarkCase("x", "A status online", frozenset({"online"}))])
        self.assertEqual(report["recall_at_k"], 1.0)


if __name__ == "__main__":
    unittest.main()
