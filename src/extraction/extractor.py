import json
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "source_chunks.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "evidence.json"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:8b"


def extract_evidence(question, chunk, source_title):
    """Ask the local LLM to extract evidence from one source chunk."""

    prompt = f"""
You are an evidence extraction system for an AI research project.

Research question:
{question}

Source:
{source_title}

Source text:
{chunk}

Your task is to determine whether this source text contains
useful evidence for answering the research question.

Return ONLY valid JSON in exactly this format:

{{
    "claim": "A concise factual claim supported by the source, or an empty string if there is no useful evidence.",
    "evidence": "The specific information from the source that supports the claim, or an empty string if there is no useful evidence.",
    "confidence": 0.0
}}

Rules:

1. Do not invent information.
2. The claim must be supported by the provided source text.
3. The evidence must come from the provided source text.
4. If the source text is irrelevant, return empty claim and evidence.
5. Confidence must be a number between 0.0 and 1.0.
6. Return ONLY JSON.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=120,
        )

        response.raise_for_status()

        result = response.json()

        raw_response = result.get("response", "{}")

        return json.loads(raw_response)

    except Exception as error:
        print(f"Extraction failed: {error}")

        return {
            "claim": "",
            "evidence": "",
            "confidence": 0.0,
        }


def run_extraction():
    """Extract evidence from every source chunk."""

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    output = {
        "question": data["question"],
        "subquestions": [],
    }

    total_chunks = 0
    successful_extractions = 0

    for subquestion in data["subquestions"]:
        question = subquestion["question"]

        print("\n" + "=" * 70)
        print("Research sub-question:")
        print(question)

        extracted_sources = []

        for source in subquestion.get("sources", []):
            title = source.get("title", "")
            url = source.get("url", "")
            chunks = source.get("chunks", [])

            print(f"\nSource: {title}")
            print(f"Chunks: {len(chunks)}")

            source_evidence = []

            for chunk_index, chunk in enumerate(chunks):
                total_chunks += 1

                print(
                    f"  Extracting chunk "
                    f"{chunk_index + 1}/{len(chunks)}..."
                )

                result = extract_evidence(
                    question,
                    chunk,
                    title,
                )

                claim = result.get("claim", "")
                evidence = result.get("evidence", "")
                confidence = result.get("confidence", 0.0)

                if claim and evidence:
                    successful_extractions += 1

                source_evidence.append(
                    {
                        "chunk_id": chunk_index,
                        "claim": str(claim).strip(),
                        "evidence": str(evidence).strip(),
                        "confidence": float(confidence),
                    }
                )

            extracted_sources.append(
                {
                    "title": title,
                    "url": url,
                    "evidence": source_evidence,
                }
            )

        output["subquestions"].append(
            {
                "question": question,
                "sources": extracted_sources,
            }
        )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print("\n" + "=" * 70)
    print("EXTRACTION SUMMARY")
    print("=" * 70)
    print(f"Total chunks processed:     {total_chunks}")
    print(f"Chunks with evidence:       {successful_extractions}")
    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_extraction()