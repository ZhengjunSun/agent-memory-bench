# Memory lifecycle and benchmark contract

```mermaid
sequenceDiagram
  participant Agent
  participant Extractor
  participant Store as Append-only SQLite memory
  participant Retriever as Hybrid retriever
  participant Bench as Benchmark evaluator
  Agent->>Extractor: conversation event
  Extractor->>Store: entity/key/value + validity
  Store->>Store: link superseded fact
  Agent->>Retriever: query + optional as-of time
  Retriever->>Store: lexical/entity/recency search
  Retriever-->>Agent: budgeted memories + scores
  Bench->>Retriever: current/historical/unknown cases
  Bench-->>Bench: Recall@K, MRR, abstention, p95
```

## Benchmark rules

- Current and historical facts are scored separately through `as_of` queries.
- Superseded facts remain available for historical questions.
- Unknown questions reward abstention rather than plausible fabrication.
- Retrieval metrics are deterministic; latency is reported independently.
- Synthetic entity names prevent contamination by memorized public facts.

