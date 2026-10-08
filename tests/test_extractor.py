import json
from unittest.mock import Mock, patch

from src.extraction.extractor import extract_evidence


def test_extract_evidence_returns_valid_evidence():
    mock_response = Mock()

    mock_response.json.return_value = {
        "response": json.dumps(
            {
                "claim": "AI agents can automate repetitive software development tasks.",
                "evidence": "The source describes AI agents automating repetitive coding activities.",
                "confidence": 0.9,
            }
        )
    }

    with patch(
        "src.extraction.extractor.requests.post",
        return_value=mock_response,
    ):
        result = extract_evidence(
            "How are AI agents changing software engineering?",
            "AI agents can automate repetitive coding activities.",
            "Example Source",
        )

    assert result["claim"] == (
        "AI agents can automate repetitive software development tasks."
    )
    assert result["evidence"] == (
        "The source describes AI agents automating repetitive coding activities."
    )
    assert result["confidence"] == 0.9


def test_extract_evidence_handles_empty_evidence():
    mock_response = Mock()

    mock_response.json.return_value = {
        "response": json.dumps(
            {
                "claim": "",
                "evidence": "",
                "confidence": 0.0,
            }
        )
    }

    with patch(
        "src.extraction.extractor.requests.post",
        return_value=mock_response,
    ):
        result = extract_evidence(
            "How are AI agents changing software engineering?",
            "This text is unrelated to the research topic.",
            "Unrelated Source",
        )

    assert result["claim"] == ""
    assert result["evidence"] == ""
    assert result["confidence"] == 0.0


def test_extract_evidence_handles_request_failure():
    with patch(
        "src.extraction.extractor.requests.post",
        side_effect=Exception("Ollama unavailable"),
    ):
        result = extract_evidence(
            "Research question",
            "Source text",
            "Example Source",
        )

    assert result == {
        "claim": "",
        "evidence": "",
        "confidence": 0.0,
    }


def test_extract_evidence_sends_expected_request():
    mock_response = Mock()

    mock_response.json.return_value = {
        "response": json.dumps(
            {
                "claim": "Test claim",
                "evidence": "Test evidence",
                "confidence": 0.8,
            }
        )
    }

    with patch(
        "src.extraction.extractor.requests.post",
        return_value=mock_response,
    ) as mock_post:

        extract_evidence(
            "Research question",
            "Source text",
            "Example Source",
        )

    mock_post.assert_called_once()

    args, kwargs = mock_post.call_args

    assert args[0] == "http://localhost:11434/api/generate"
    assert kwargs["json"]["model"] == "qwen3:8b"
    assert kwargs["json"]["stream"] is False
    assert kwargs["json"]["format"] == "json"
    assert kwargs["timeout"] == 120