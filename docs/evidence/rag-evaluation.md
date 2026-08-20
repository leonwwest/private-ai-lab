# Offline RAG retrieval evidence

This evidence is generated with synthetic documents and the deterministic hash embedding provider. It performs no network calls and uses no private PDFs or API keys.

- Dataset: `synthetic-private-ai-contract-v1`
- Embedding dimensions: 128
- Queries: 3
- Top-1 accuracy: 100.00%
- Mean reciprocal rank: 1.0000

| Question | Expected | Retrieved | Rank | Score |
|---|---|---|---:|---:|
| Which bearer API key authentication protects the document upload endpoint? | `authentication` | `authentication` | 1 | 0.7535 |
| Why does readyz report failure when the Postgres database is unavailable? | `operations` | `operations` | 1 | 0.5153 |
| Does uploaded PDF content stay local and out of structured logs? | `privacy` | `privacy` | 1 | 0.3325 |

The synthetic evaluation proves retrieval wiring and regression stability. It is not a claim about answer quality on private or production document collections.
