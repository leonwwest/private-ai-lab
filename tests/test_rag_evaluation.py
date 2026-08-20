import asyncio
import json
from pathlib import Path

from tools.rag_evaluation import evaluate, render_markdown

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "fixtures" / "rag-evaluation.json").read_text())


def test_synthetic_retrieval_finds_every_expected_document() -> None:
    result = asyncio.run(evaluate(CONFIG))

    assert result["top_1_accuracy"] == 1.0
    assert result["mean_reciprocal_rank"] == 1.0
    assert [case["expected_rank"] for case in result["results"]] == [1, 1, 1]


def test_evaluation_evidence_is_deterministic_and_explicitly_synthetic() -> None:
    first = render_markdown(asyncio.run(evaluate(CONFIG)))
    second = render_markdown(asyncio.run(evaluate(CONFIG)))

    assert first == second
    assert "Top-1 accuracy: 100.00%" in first
    assert "Mean reciprocal rank: 1.0000" in first
    assert "synthetic documents" in first
    assert "no private PDFs or API keys" in first
