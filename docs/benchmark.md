# Synthetic smoke benchmark (not generalization evidence)

The figures below are historical smoke-test results. Queries use exact synthetic entity names. All no-answer cases repeat the same unrelated phrase (`lunar outpost steward`), so abstention accuracy does not measure difficult negatives. Expected answers are repeated team values rather than unique fact IDs, which can accept the wrong entity with the same owner. Do not advertise these scores as real conversational-memory accuracy.

A replacement evaluation needs unique evidence IDs, similar-but-unknown entities, paraphrases, temporal updates, baselines, and per-query failures. That replacement has not yet been implemented.

## Historical run

Measured on 2026-10-08 with Python 3.12 on a local Windows workstation, an in-memory SQLite database, 1,000 synthetic facts, and 200 queries. Ten percent of the queries are deliberately unknown abstention cases.

| Metric | Result |
|---|---:|
| Recall@3 | 1.0000 |
| MRR | 1.0000 |
| Abstention accuracy | 1.0000 |
| P95 retrieval latency | 11.8278 ms |

Reproduce with `python scripts/benchmark_scale.py --facts 1000 --queries 200`.

The benchmark is deterministic except for wall-clock latency. It is a synthetic regression suite, not evidence that the retriever generalizes to arbitrary conversations. A production evaluation should add paraphrases, ambiguous entities, conflicting sources, multilingual queries, and larger stores.
