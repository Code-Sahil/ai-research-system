from unittest.mock import patch, Mock

from src.planner.planner import create_research_plan


def test_create_research_plan_returns_subquestions():
    mock_response = Mock()
    mock_response.message.content = """
How do AI agents automate repetitive tasks?
What role do AI agents play in code generation?
How are human-AI collaboration patterns changing?
What impact do AI agents have on software quality?
What skills are required for AI-assisted software engineering?
"""

    with patch("src.planner.planner.chat", return_value=mock_response):
        result = create_research_plan(
            "How are AI agents changing software engineering?"
        )

    assert isinstance(result, list)
    assert len(result) == 5


def test_create_research_plan_returns_strings():
    mock_response = Mock()
    mock_response.message.content = """
How do AI agents automate repetitive tasks?
What role do AI agents play in code generation?
What impact do AI agents have on software quality?
"""

    with patch("src.planner.planner.chat", return_value=mock_response):
        result = create_research_plan(
            "How are AI agents changing software engineering?"
        )

    assert all(isinstance(item, str) for item in result)


def test_create_research_plan_removes_numbering():
    mock_response = Mock()
    mock_response.message.content = """
1. How do AI agents automate repetitive tasks?
2. What role do AI agents play in code generation?
3. What impact do AI agents have on software quality?
"""

    with patch("src.planner.planner.chat", return_value=mock_response):
        result = create_research_plan(
            "How are AI agents changing software engineering?"
        )

    assert result == [
        "How do AI agents automate repetitive tasks?",
        "What role do AI agents play in code generation?",
        "What impact do AI agents have on software quality?",
    ]


def test_create_research_plan_ignores_empty_lines():
    mock_response = Mock()
    mock_response.message.content = """
How do AI agents automate repetitive tasks?


What role do AI agents play in code generation?

What impact do AI agents have on software quality?

"""

    with patch("src.planner.planner.chat", return_value=mock_response):
        result = create_research_plan(
            "How are AI agents changing software engineering?"
        )

    assert len(result) == 3
    assert all(item.strip() for item in result)