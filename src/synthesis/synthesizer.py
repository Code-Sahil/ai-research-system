import json
from pathlib import Path

from ollama import chat


# =========================================================
# Configuration
# =========================================================

MODEL = "qwen3:8b"

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "filtered_evidence.json"
OUTPUT_FILE = BASE_DIR / "data" / "research_report.md"


# =========================================================
# Load evidence
# =========================================================

def load_evidence() -> dict:
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


# =========================================================
# Prepare evidence for the model
# =========================================================

def build_evidence_text(data: dict) -> str:
    sections = []

    for subquestion_data in data.get("subquestions", []):
        subquestion = subquestion_data.get("question", "")
        sources = subquestion_data.get("sources", [])

        sections.append(
            f"\n{'=' * 70}\n"
            f"RESEARCH SUB-QUESTION\n"
            f"{subquestion}\n"
            f"{'=' * 70}\n"
        )

        if not sources:
            sections.append(
                "NO ACCEPTED EVIDENCE WAS FOUND FOR THIS SUB-QUESTION.\n"
            )
            continue

        for source_index, source in enumerate(sources, start=1):
            title = source.get("title", "")
            url = source.get("url", "")

            evaluation = source.get("evaluation", {})

            relevance = evaluation.get("relevance", 0)
            quality = evaluation.get("quality", 0)
            reason = evaluation.get("reason", "")

            evidence_items = source.get("evidence", [])

            sections.append(
                f"""
SOURCE {source_index}
Title: {title}
URL: {url}

Source evaluation:
Relevance: {relevance}
Quality: {quality}
Reason: {reason}
"""
            )

            if not evidence_items:
                sections.append(
                    "No evidence items were retained from this source.\n"
                )
                continue

            for evidence_index, evidence in enumerate(
                evidence_items,
                start=1,
            ):
                sections.append(
                    f"""
Evidence item {evidence_index}:

Claim:
{evidence.get("claim", "")}

Evidence:
{evidence.get("evidence", "")}

Confidence:
{evidence.get("confidence", 0)}
"""
                )

    return "\n".join(sections)


# =========================================================
# Build synthesis prompt
# =========================================================

def build_prompt(data: dict) -> str:
    question = data.get("question", "")
    subquestions = data.get("subquestions", [])

    evidence_text = build_evidence_text(data)

    section_instructions = []

    for index, subquestion_data in enumerate(
        subquestions,
        start=1,
    ):
        subquestion = subquestion_data.get("question", "")

        section_instructions.append(
            f"""## {index}. {subquestion}

Discuss ONLY evidence relevant to this sub-question.

Do not answer this section using evidence belonging primarily
to another sub-question.
"""
        )

    sections = "\n".join(section_instructions)

    prompt = f"""
You are the synthesis component of an AI research system.

RESEARCH QUESTION
{question}

You have been given a dataset containing evaluated and filtered
research evidence.

Your task is to produce a rigorous research report using ONLY
that evidence dataset.

============================================================
ABSOLUTE EVIDENCE CONSTRAINT
============================================================

The evidence dataset is the ONLY source of information available
to you for this report.

Do not use your pretrained knowledge.

Do not add facts because they are generally known.

Do not add examples, statistics, studies, organizations,
technologies, claims, or conclusions that do not appear in the
dataset.

If the dataset does not support a claim, do not make the claim.

============================================================
EVIDENCE RULES
============================================================

1. Use ONLY the supplied evidence.

2. Every factual claim must be traceable to supplied evidence.

3. Prefer evidence with:
   - higher confidence
   - higher relevance
   - higher source quality

4. Do not present low-confidence evidence as established fact.

5. If evidence conflicts, explicitly describe the conflict.

6. If a sub-question has no accepted evidence, write:

"The available evidence in this dataset is insufficient to
answer this sub-question."

7. Do not manufacture an answer for a sub-question merely because
you know something about the topic.

8. Keep evidence and interpretation distinct.

9. Recommendations must be clearly identified as recommendations
derived from the evidence.

10. Do not turn correlation into causation.

============================================================
AI TERMINOLOGY
============================================================

Preserve the distinction between:

- generative AI tools
- AI assistants
- AI agents
- autonomous or agentic systems

Do not call an ordinary AI coding assistant an autonomous agent
unless the supplied evidence supports that characterization.

============================================================
SOURCE TRACEABILITY
============================================================

Important factual claims must include inline source citations.

Use EXACTLY:

[Source: TITLE]

For multiple supporting sources:

[Sources: TITLE 1; TITLE 2]

Do not use:

[Source 1]
[Source 2]
[Evidence 3]

unless those labels are explicitly defined by the report.

At the end, include every source actually used.

Use:

- TITLE — URL

Never invent a URL.

============================================================
REPORT STRUCTURE
============================================================

Write exactly this structure:

# {question}

## Executive Summary

Summarize only the strongest supported findings across the
dataset.

Do not introduce information not present in the evidence.

{sections}

## Overall Assessment

Synthesize the strongest supported findings across the research
question.

Clearly distinguish:

- well-supported findings
- weaker findings
- areas where evidence is insufficient

Do not introduce new evidence in this section.

## Limitations

Discuss limitations visible in the supplied dataset, including:

- missing evidence
- weak source quality
- low-confidence evidence
- limited source coverage
- conflicting evidence
- concentration of evidence around particular sources

Do not invent limitations that cannot be inferred from the
dataset.

## Sources

List every source actually used.

Format:

- Title — URL

============================================================
WRITING STYLE
============================================================

Write a coherent research report.

Do NOT simply summarize each source separately.

Synthesize overlapping evidence.

For example, prefer:

"Several sources indicate that AI-assisted development is
automating repetitive coding and testing tasks..."

rather than:

"Source A says X. Source B says Y. Source C says Z."

However, preserve source traceability using the required
[Source: ...] notation.

Do not exaggerate findings.

Do not use unsupported superlatives such as "revolutionary",
"massive", "profound", or "fundamental" unless the evidence
itself supports such characterization.

Do not add recommendations unless they are explicitly derived
from the supplied evidence.

============================================================
SUB-QUESTION DISCIPLINE
============================================================

Each numbered section must answer ONLY its corresponding
sub-question.

Do not move evidence between sections simply because it is
topically related.

If evidence is missing for a section, say so explicitly.

============================================================
EVIDENCE DATASET
============================================================

{evidence_text}
"""

    return prompt


# =========================================================
# Generate report
# =========================================================

def synthesize(data: dict) -> str:
    prompt = build_prompt(data)

    print("\nGenerating research report...\n")

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]


# =========================================================
# Save report
# =========================================================

def save_report(report: str) -> None:
    OUTPUT_FILE.write_text(
        report,
        encoding="utf-8",
    )

    print(f"Research report saved to: {OUTPUT_FILE}")


# =========================================================
# Main
# =========================================================

def main() -> None:
    print("=" * 70)
    print("AI RESEARCH SYSTEM — SYNTHESIS")
    print("=" * 70)

    data = load_evidence()

    print("\nResearch question:")
    print(data["question"])

    print(
        f"\nSubquestions: "
        f"{len(data.get('subquestions', []))}"
    )

    report = synthesize(data)

    save_report(report)

    print("\nSynthesis complete.")


if __name__ == "__main__":
    main()