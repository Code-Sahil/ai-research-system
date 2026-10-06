import json
from pathlib import Path


CONFIDENCE_THRESHOLD = 0.5


def load_evidence() -> dict:
    project_root = Path(__file__).resolve().parents[2]
    evidence_file = project_root / "data" / "evidence.json"

    with evidence_file.open("r", encoding="utf-8") as file:
        return json.load(file)


def filter_sources(sources: list) -> list:
    """
    Keep only usable evidence.

    A source is kept only when:
    - confidence >= 0.5
    - claim is not empty
    - evidence is not empty
    - URL has not already been seen
    """

    filtered_sources = []
    seen_urls = set()

    for source in sources:
        evidence = source.get("evidence", {})

        claim = str(evidence.get("claim", "")).strip()
        extracted_evidence = str(
            evidence.get("evidence", "")
        ).strip()

        confidence = evidence.get("confidence", 0)

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0

        url = source.get("url", "").strip()

        # Reject low-confidence evidence.
        if confidence < CONFIDENCE_THRESHOLD:
            continue

        # Reject sources with no extracted claim.
        if not claim:
            continue

        # Reject sources with no extracted evidence.
        if not extracted_evidence:
            continue

        # Reject duplicate URLs.
        if url and url in seen_urls:
            continue

        if url:
            seen_urls.add(url)

        filtered_sources.append(source)

    return filtered_sources


def run_filter() -> dict:
    data = load_evidence()

    filtered_data = {
        "question": data["question"],
        "subquestions": [],
    }

    for subquestion_data in data["subquestions"]:
        question = subquestion_data["question"]

        original_sources = subquestion_data.get(
            "sources", []
        )

        filtered_sources = filter_sources(
            original_sources
        )

        filtered_data["subquestions"].append(
            {
                "question": question,
                "sources": filtered_sources,
                "source_count": len(filtered_sources),
            }
        )

        print("\n" + "=" * 70)
        print(f"Sub-question:")
        print(question)

        print(
            f"Sources before filtering: "
            f"{len(original_sources)}"
        )

        print(
            f"Sources after filtering:  "
            f"{len(filtered_sources)}"
        )

        if not filtered_sources:
            print(
                "WARNING: No usable evidence found."
            )

    return filtered_data


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]

    output_file = (
        project_root
        / "data"
        / "filtered_evidence.json"
    )

    results = run_filter()

    output_file.write_text(
        json.dumps(
            results,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\n" + "=" * 70)
    print(f"Saved to: {output_file}")