import json
from pathlib import Path

from ollama import chat


MODEL = "qwen3:8b"


def load_sources() -> dict:
    project_root = Path(__file__).resolve().parents[2]
    sources_file = project_root / "data" / "sources.json"

    with sources_file.open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate_source(
    research_question: str,
    subquestion: str,
    source: dict,
) -> dict:
    prompt = f"""
You are evaluating a source for an AI research system.

Research question:
{research_question}

Research sub-question:
{subquestion}

Source title:
{source.get("title", "")}

Source URL:
{source.get("url", "")}

Source snippet:
{source.get("snippet", "")}

Evaluate how useful this source is for answering the research
sub-question.

Give:
1. A relevance score from 0 to 1.
2. A quality score from 0 to 1.
3. A brief reason.

Return ONLY valid JSON in exactly this format:

{{
    "relevance": 0.0,
    "quality": 0.0,
    "reason": "..."
}}
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

    content = response.message.content.strip()

    try:
        evaluation = json.loads(content)
    except json.JSONDecodeError:
        evaluation = {
            "relevance": 0.0,
            "quality": 0.0,
            "reason": "The model returned invalid JSON.",
        }

    return evaluation


def run_evaluation() -> dict:
    data = load_sources()

    evaluated_data = {
        "question": data["question"],
        "subquestions": [],
    }

    for subquestion_data in data["subquestions"]:
        subquestion = subquestion_data["question"]

        print(f"\n{'=' * 70}")
        print(f"Evaluating: {subquestion}")

        evaluated_sources = []

        for source in subquestion_data["sources"]:
            print(f"\nSource: {source.get('title')}")

            evaluation = evaluate_source(
                data["question"],
                subquestion,
                source,
            )

            source_with_evaluation = {
                **source,
                "evaluation": evaluation,
            }

            evaluated_sources.append(source_with_evaluation)

            print(
                f"Relevance: {evaluation.get('relevance')}"
            )
            print(
                f"Quality: {evaluation.get('quality')}"
            )

        evaluated_sources.sort(
            key=lambda source: (
                source["evaluation"].get("relevance", 0)
                + source["evaluation"].get("quality", 0)
            ),
            reverse=True,
        )

        evaluated_data["subquestions"].append(
            {
                "question": subquestion,
                "search_queries": subquestion_data.get(
                    "search_queries", []
                ),
                "sources": evaluated_sources,
            }
        )

    return evaluated_data


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]

    output_file = project_root / "data" / "evaluated_sources.json"

    results = run_evaluation()

    output_file.write_text(
        json.dumps(
            results,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"\nSaved to: {output_file}")