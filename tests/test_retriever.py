from unittest.mock import Mock, patch

from src.retrieval.retriever import (
    generate_search_queries,
    search_web,
)


def test_generate_search_queries_returns_expected_number():
    mock_response = Mock()
    mock_response.message.content = """
AI agents repetitive software engineering tasks research
AI automation of repetitive coding tasks studies
AI agents software development automation technical reports
AI agents repetitive tasks software engineering
"""

    with patch("src.retrieval.retriever.chat", return_value=mock_response):
        result = generate_search_queries(
            "How do AI agents automate repetitive tasks in software development?",
            number_of_queries=3,
        )

    assert isinstance(result, list)
    assert len(result) == 3


def test_generate_search_queries_removes_numbering():
    mock_response = Mock()
    mock_response.message.content = """
1. AI agents automate repetitive coding tasks
2. AI automation software development research
3. AI agents repetitive tasks technical reports
"""

    with patch("src.retrieval.retriever.chat", return_value=mock_response):
        result = generate_search_queries(
            "How do AI agents automate repetitive tasks in software development?",
            number_of_queries=3,
        )

    assert result == [
        "AI agents automate repetitive coding tasks",
        "AI automation software development research",
        "AI agents repetitive tasks technical reports",
    ]


def test_search_web_returns_expected_source_structure():
    mock_search_results = [
        {
            "title": "AI in Software Engineering",
            "href": "https://example.com/ai",
            "body": "AI agents are changing software engineering.",
        },
        {
            "title": "AI Coding Agents",
            "href": "https://example.com/agents",
            "body": "AI agents can automate coding tasks.",
        },
    ]

    mock_ddgs_instance = Mock()
    mock_ddgs_instance.text.return_value = mock_search_results

    with patch(
        "src.retrieval.retriever.DDGS",
        return_value=mock_ddgs_instance,
    ):
        result = search_web(
            "AI agents software engineering",
            max_results=5,
        )

    assert len(result) == 2

    assert result[0] == {
        "title": "AI in Software Engineering",
        "url": "https://example.com/ai",
        "snippet": "AI agents are changing software engineering.",
    }

    assert result[1] == {
        "title": "AI Coding Agents",
        "url": "https://example.com/agents",
        "snippet": "AI agents can automate coding tasks.",
    }


def test_search_web_handles_search_failure():
    from ddgs.exceptions import DDGSException

    mock_ddgs_instance = Mock()
    mock_ddgs_instance.text.side_effect = DDGSException("Search failed")

    with patch(
        "src.retrieval.retriever.DDGS",
        return_value=mock_ddgs_instance,
    ):
        result = search_web("AI agents software engineering")

    assert result == []