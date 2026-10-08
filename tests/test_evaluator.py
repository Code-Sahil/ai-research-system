import json
from unittest.mock import Mock, patch

from src.evaluation.evaluator import (
    combine_chunks,
    evaluate_source,
)


def test_combine_chunks_formats_chunks():
    chunks = [
        "First chunk of source text.",
        "Second chunk of source text.",
    ]

    result = combine_chunks(chunks)

    assert result == (
        "[Chunk 1]\nFirst chunk of source text.\n\n"
        "[Chunk 2]\nSecond chunk of source text."
    )


def test_combine_chunks_handles_empty_list():
    result = combine_chunks([])

    assert result == ""


def test_evaluate_source_returns_valid_evaluation():
    mock_response = Mock()

    mock_response.message.content = json.dumps(
        {
            "relevance": 0.9,
            "quality": 0.8,
            "reason": "The source directly addresses the research question.",
        }
    )

    source = {
        "title": "AI Agents in Software Engineering",
        "url": "https://example.com/article",
        "chunks": [
            "AI agents can automate software development tasks.",
            "Agents can also assist with debugging and testing.",
        ],
    }

    with patch(
        "src.evaluation.evaluator.chat",
        return_value=mock_response,
    ):
        result = evaluate_source(
            "How are AI agents changing software engineering?",
            "What role do AI agents play in code generation?",
            source,
        )

    assert result["relevance"] == 0.9
    assert result["quality"] == 0.8
    assert isinstance(result["reason"], str)


def test_evaluate_source_handles_invalid_json():
    mock_response = Mock()
    mock_response.message.content = "This is not valid JSON."

    source = {
        "title": "Example Source",
        "url": "https://example.com",
        "chunks": ["Some source content."],
    }

    with patch(
        "src.evaluation.evaluator.chat",
        return_value=mock_response,
    ):
        result = evaluate_source(
            "Research question",
            "Research sub-question",
            source,
        )

    assert result["relevance"] == 0.0
    assert result["quality"] == 0.0
    assert result["reason"] == "The model returned invalid JSON."