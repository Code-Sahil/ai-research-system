import json
from pathlib import Path

from ddgs import DDGS
from ddgs.exceptions import DDGSException
from ollama import chat


MODEL = "qwen3:8b"


def load_research_plan() -> dict:
    project_root = Path(__file__).resolve().parents[2]
    plan_file = project_root / "data" / "research_plan.json"

    with plan_file.open("r", encoding="utf-8") as file:
        return json.load(file)


def generate_search_queries(subquestion: str, number_of_queries: int = 3) -> list[str]:
    prompt = f"""
You are a research search-query generator.

Given the research sub-question below, generate exactly
{number_of_queries} concise web search queries.

The queries should use different wording and focus on finding
reliable research, reports, studies, technical documentation,
or authoritative sources.

Do not answer the question.

Return ONLY the search queries, one per line.
Do not number them.

Research sub-question:
{subquestion}
"""

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    lines = response.message.content.strip().splitlines()

    queries = []

    for line in lines:
        line = line.strip()
        line = line.lstrip("0123456789.-) ").strip()

        if line:
            queries.append(line)

    return queries[:number_of_queries]


def search_web(query: str, max_results: int = 5) -> list[dict]:
    ddgs = DDGS()

    try:
        search_results = ddgs.text(
            query,
            max_results=max_results,
        )

    except DDGSException as error:
        print(f"Search failed: {error}")
        return []

    results = []

    for result in search_results:
        results.append(
            {
                "title": result.get("title"),
                "url": result.get("href"),
                "snippet": result.get("body"),
            }
        )

    return results


def run_retrieval() -> dict:
    research_plan = load_research_plan()

    research_results = {
        "question": research_plan["question"],
        "subquestions": [],
    }

    for subquestion in research_plan["subquestions"]:
        print(f"\n{'=' * 70}")
        print(f"Research sub-question:\n{subquestion}")

        print("\nGenerating search queries...")

        queries = generate_search_queries(subquestion)

        for query in queries:
            print(f"  → {query}")

        all_sources = []

        for query in queries:
            print(f"\nSearching: {query}")

            sources = search_web(query)

            print(f"Found {len(sources)} sources.")

            for source in sources:
                source["search_query"] = query
                all_sources.append(source)

        research_results["subquestions"].append(
            {
                "question": subquestion,
                "search_queries": queries,
                "sources": all_sources,
            }
        )

    return research_results


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]

    output_file = project_root / "data" / "sources.json"

    results = run_retrieval()

    output_file.write_text(
        json.dumps(
            results,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"\nSaved to: {output_file}")