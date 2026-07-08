import pytest

from app.services.chunking import chunk_text, normalize_text


def test_normalize_text_collapses_whitespace() -> None:
    assert normalize_text("a\n\n b\t c") == "a b c"


def test_chunk_text_uses_overlap() -> None:
    text = " ".join(f"w{i}" for i in range(10))
    chunks = chunk_text(text, max_tokens=4, overlap_tokens=1)

    assert [chunk.token_count for chunk in chunks] == [4, 4, 4]
    assert chunks[0].content == "w0 w1 w2 w3"
    assert chunks[1].content == "w3 w4 w5 w6"
    assert chunks[2].content == "w6 w7 w8 w9"


def test_chunk_text_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        chunk_text("hello", max_tokens=10, overlap_tokens=10)
