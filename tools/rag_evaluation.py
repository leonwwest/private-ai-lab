from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

from app.services.embeddings import HashEmbeddingProvider

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "fixtures" / "rag-evaluation.json"
DEFAULT_OUTPUT = ROOT / "docs" / "evidence" / "rag-evaluation.md"


@dataclass(frozen=True)
class RankedDocument:
    document_id: str
    score: float


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(
        left_value * right_value
        for left_value, right_value in zip(left, right, strict=True)
    )


async def evaluate(config: dict) -> dict:
    dimensions = int(config["dimensions"])
    documents = config["documents"]
    queries = config["queries"]
    provider = HashEmbeddingProvider(dimensions=dimensions)
    document_vectors = await provider.embed([document["text"] for document in documents])

    results = []
    reciprocal_rank_total = 0.0
    top_one_hits = 0
    for query in queries:
        query_vector = (await provider.embed([query["question"]]))[0]
        ranking = sorted(
            (
                RankedDocument(
                    document_id=document["id"],
                    score=cosine_similarity(query_vector, document_vector),
                )
                for document, document_vector in zip(documents, document_vectors, strict=True)
            ),
            key=lambda item: (-item.score, item.document_id),
        )
        expected_rank = next(
            index
            for index, document in enumerate(ranking, start=1)
            if document.document_id == query["expected_document_id"]
        )
        reciprocal_rank_total += 1.0 / expected_rank
        top_one_hits += int(expected_rank == 1)
        results.append(
            {
                "question": query["question"],
                "expected_document_id": query["expected_document_id"],
                "top_document_id": ranking[0].document_id,
                "expected_rank": expected_rank,
                "top_score": round(ranking[0].score, 4),
            }
        )

    query_count = len(queries)
    return {
        "dataset": config["name"],
        "dimensions": dimensions,
        "query_count": query_count,
        "top_1_accuracy": top_one_hits / query_count,
        "mean_reciprocal_rank": reciprocal_rank_total / query_count,
        "results": results,
    }


def render_markdown(result: dict) -> str:
    rows = [
        "# Offline RAG retrieval evidence",
        "",
        (
            "This evidence is generated with synthetic documents and the deterministic "
            "hash embedding provider. It performs no network calls and uses no private PDFs "
            "or API keys."
        ),
        "",
        f"- Dataset: `{result['dataset']}`",
        f"- Embedding dimensions: {result['dimensions']}",
        f"- Queries: {result['query_count']}",
        f"- Top-1 accuracy: {result['top_1_accuracy']:.2%}",
        f"- Mean reciprocal rank: {result['mean_reciprocal_rank']:.4f}",
        "",
        "| Question | Expected | Retrieved | Rank | Score |",
        "|---|---|---|---:|---:|",
    ]
    rows.extend(
        (
            "| {question} | `{expected_document_id}` | `{top_document_id}` | "
            "{expected_rank} | {top_score:.4f} |"
        ).format(
            **case
        )
        for case in result["results"]
    )
    rows.extend(
        [
            "",
            (
                "The synthetic evaluation proves retrieval wiring and regression stability. "
                "It is not a claim about answer quality on private or production document "
                "collections."
            ),
            "",
        ]
    )
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic offline RAG evaluation")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = json.loads(args.config.read_text())
    result = asyncio.run(evaluate(config))
    evidence = render_markdown(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(evidence)
    print(evidence)


if __name__ == "__main__":
    main()
