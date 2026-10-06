import json
from pathlib import Path

from ollama import chat


MODEL = "qwen3:8b"


def create_research_plan(question: str) -> list[str]:
    prompt = f"""
You are the planning component of an AI research system.

Break the following research question into 5-7 specific
research sub-questions.

Avoid redundant questions.

Return ONLY the sub-questions, one per line.
Do not include numbering.

Research question:
{question}
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

    subquestions = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Remove numbering if the model adds it anyway.
        line = line.lstrip("0123456789.-) ").strip()

        if line:
            subquestions.append(line)

    return subquestions


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]

    question_file = project_root / "experiments" / "questions.txt"
    output_file = project_root / "data" / "research_plan.json"

    question = question_file.read_text(encoding="utf-8").strip()

    print("\nResearch Question:")
    print(question)

    print("\nGenerating research plan...\n")

    subquestions = create_research_plan(question)

    research_plan = {
        "question": question,
        "subquestions": subquestions,
    }

    output_file.write_text(
        json.dumps(research_plan, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    print("Research Plan:")

    for i, subquestion in enumerate(subquestions, start=1):
        print(f"{i}. {subquestion}")

    print(f"\nSaved to: {output_file}")