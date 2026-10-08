from unittest.mock import Mock, patch

from src.synthesis.synthesizer import (
    build_evidence_text,
    build_prompt,
    synthesize,
)


def sample_data():
    return {
        "question": "How are AI agents changing software engineering?",
        "subquestions": [
            {
                "question": "How do AI agents automate repetitive tasks?",
                "sources": [
                    {
                        "title": "Example AI Source",
                        "url": "https://example.com/source",
                        "evaluation": {
                            "relevance": 0.9,
                            "quality": 0.8,
                            "reason": "Relevant technical source.",
                        },
                        "evidence": [
                            {
                                "claim": "AI agents automate repetitive tasks.",
                                "evidence": "The source describes automated coding tasks.",
                                "confidence": 0.95,
                            }
                        ],
                    }
                ],
            }
        ],
    }


def test_build_evidence_text_contains_source_and_evidence():
    data = sample_data()

    result = build_evidence_text(data)

    assert "Example AI Source" in result
    assert "https://example.com/source" in result
    assert "AI agents automate repetitive tasks." in result
    assert "The source describes automated coding tasks." in result
    assert "0.95" in result


def test_build_evidence_text_handles_missing_evidence():
    data = {
        "question": "Test question",
        "subquestions": [
            {
                "question": "Test subquestion",
                "sources": [],
            }
        ],
    }

    result = build_evidence_text(data)

    assert "NO ACCEPTED EVIDENCE WAS FOUND" in result


def test_build_prompt_contains_research_question_and_constraints():
    data = sample_data()

    result = build_prompt(data)

    assert "How are AI agents changing software engineering?" in result
    assert "How do AI agents automate repetitive tasks?" in result
    assert "Use ONLY the supplied evidence." in result
    assert "[Source: TITLE]" in result
    assert "Do not use your pretrained knowledge." in result


def test_synthesize_returns_model_response():
    mock_response = Mock()
    mock_response.__getitem__ = Mock(
        side_effect=lambda key: (
            {
                "message": {
                    "content": "# AI Research Report\n\nAI agents can automate repetitive tasks."
                }
            }[key]
        )
    )

    data = sample_data()

    with patch(
        "src.synthesis.synthesizer.chat",
        return_value=mock_response,
    ):
        result = synthesize(data)

    assert result == (
        "# AI Research Report\n\n"
        "AI agents can automate repetitive tasks."
    )