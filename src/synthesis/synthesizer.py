import json
from pathlib import Path

from ollama import chat


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MODEL = "qwen3:8b"

BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_FILE = BASE_DIR / "data" / "filtered_evidence.json"
OUTPUT_FILE = BASE_DIR / "data" / "research_report.md"


# ---------------------------------------------------------
# Load filtered evidence
# ---------------------------------------------------------

def load_evidence():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------
# Build synthesis prompt
# ---------------------------------------------------------

def build_prompt(data):
    question = data["question"]
    subquestions = data["subquestions"]

    evidence_sections = []

    for subquestion in subquestions:
        subq = subquestion["question"]
        sources = subquestion.get("sources", [])

        evidence_sections.append(
            f"\n## Research sub-question\n{subq}\n"
        )

        if not sources:
            evidence_sections.append(
                "NO RELIABLE EVIDENCE WAS FOUND FOR THIS SUB-QUESTION.\n"
            )
            continue

        for source in sources:
            title = source.get("title", "")
            url = source.get("url", "")

            evaluation = source.get("evaluation", {})
            relevance = evaluation.get("relevance", 0)
            quality = evaluation.get("quality", 0)

            evidence = source.get("evidence", {})
            claim = evidence.get("claim", "")
            extracted_evidence = evidence.get("evidence", "")
            confidence = evidence.get("confidence", 0)

            evidence_sections.append(
                f"""
SOURCE:
Title: {title}
URL: {url}

Relevance: {relevance}
Quality: {quality}

Claim:
{claim}

Evidence:
{extracted_evidence}

Confidence:
{confidence}
"""
            )

    evidence_text = "\n".join(evidence_sections)

    prompt = f"""
You are the synthesis component of an AI research system.

Research question:
{question}

Your task is to synthesize the provided evidence into a coherent research report.

IMPORTANT RULES:

1. Use ONLY the evidence provided below.
2. Do not invent facts, studies, statistics, examples, or conclusions.
3. Do not fill gaps using your own knowledge.
4. If a sub-question has no evidence, explicitly say that the
   available research evidence in this dataset is insufficient.
5. Give more weight to evidence with higher confidence, relevance,
   and source quality.
6. Do not treat a low-confidence claim as established fact.
7. Identify conflicting evidence if it appears.
8. Preserve the distinction between evidence and interpretation.
9. Every important factual claim should be traceable to a source.
10. Include source links in the report.
11. Write a balanced research report rather than a list of disconnected summaries.

Structure the report as:

# {question}

## Executive Summary

Provide a concise synthesis of the strongest findings.

## 1. Automation of Software Development Tasks

Discuss the evidence relevant to the first sub-question.

## 2. Code Generation and Debugging

Discuss the evidence relevant to the second sub-question.

## 3. Human-AI Collaboration

Discuss the evidence relevant to the third sub-question.
If evidence is missing, explicitly state that.

## 4. Software Quality and Reliability

Discuss the evidence relevant to the fourth sub-question.

## 5. Skills and Competencies

Discuss the evidence relevant to the fifth sub-question.

## 6. Ethical Considerations

Discuss the evidence relevant to the sixth sub-question.

## 7. Long-Term Changes in Software Engineering

Discuss the evidence relevant to the seventh sub-question.

## Overall Assessment

Synthesize the strongest conclusions across the evidence.

Clearly distinguish well-supported conclusions from weaker or
incomplete evidence.

## Limitations

Explain important limitations in the evidence set, including
missing evidence, low-confidence evidence, source quality, and
limited source coverage.

## Sources

List the sources used in the report with their titles and URLs.

Here is the evidence dataset:

{evidence_text}
"""

    return prompt


# ---------------------------------------------------------
# Generate report
# ---------------------------------------------------------

def synthesize(data):
    prompt = build_prompt(data)

    print("\nGenerating research report...\n")

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# ---------------------------------------------------------
# Save report
# ---------------------------------------------------------

def save_report(report):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Research report saved to: {OUTPUT_FILE}")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    print("=" * 70)
    print("AI RESEARCH SYSTEM — SYNTHESIS")
    print("=" * 70)

    data = load_evidence()

    print(f"\nResearch question:")
    print(data["question"])

    print(f"\nSubquestions: {len(data['subquestions'])}")

    report = synthesize(data)

    save_report(report)

    print("\nSynthesis complete.")


if __name__ == "__main__":
    main()