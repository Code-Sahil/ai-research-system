import json
from pathlib import Path


MIN_EVIDENCE_CONFIDENCE = 0.60
MIN_SOURCE_RELEVANCE = 0.50
MIN_SOURCE_QUALITY = 0.50


def load_json(file_path: Path) -> dict:
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_source_evaluation_map(evaluated_sources: dict) -> dict:
    """
    Build a lookup table:

        source URL -> evaluation

    This allows evidence extracted from a source to inherit
    that source's relevance and quality evaluation.
    """

    evaluation_map = {}

    for subquestion in evaluated_sources.get("subquestions", []):
        for source in subquestion.get("sources", []):
            url = source.get("url")

            if not url:
                continue

            evaluation_map[url] = source.get(
                "evaluation",
                {
                    "relevance": 0.0,
                    "quality": 0.0,
                    "reason": "No evaluation available.",
                },
            )

    return evaluation_map


def filter_evidence(
    evidence_data: dict,
    evaluated_sources: dict,
) -> dict:

    evaluation_map = build_source_evaluation_map(
        evaluated_sources
    )

    filtered_data = {
        "question": evidence_data["question"],
        "subquestions": [],
    }

    total_evidence = 0
    accepted_evidence = 0

    for subquestion_data in evidence_data.get(
        "subquestions", []
    ):

        subquestion = subquestion_data["question"]

        filtered_sources = []

        for source in subquestion_data.get("sources", []):

            url = source.get("url", "")

            evaluation = evaluation_map.get(
                url,
                {
                    "relevance": 0.0,
                    "quality": 0.0,
                    "reason": "Source was not evaluated.",
                },
            )

            source_relevance = evaluation.get(
                "relevance", 0.0
            )

            source_quality = evaluation.get(
                "quality", 0.0
            )

            filtered_evidence_items = []

            for evidence_item in source.get(
                "evidence", []
            ):

                total_evidence += 1

                confidence = evidence_item.get(
                    "confidence", 0.0
                )

                if not isinstance(confidence, (int, float)):
                    confidence = 0.0

                if confidence < MIN_EVIDENCE_CONFIDENCE:
                    continue

                if source_relevance < MIN_SOURCE_RELEVANCE:
                    continue

                if source_quality < MIN_SOURCE_QUALITY:
                    continue

                filtered_evidence_items.append(
                    evidence_item
                )

                accepted_evidence += 1

            if filtered_evidence_items:

                filtered_sources.append(
                    {
                        "title": source.get(
                            "title", ""
                        ),
                        "url": url,
                        "evaluation": evaluation,
                        "evidence": filtered_evidence_items,
                    }
                )

        filtered_data["subquestions"].append(
            {
                "question": subquestion,
                "sources": filtered_sources,
            }
        )

    print("\n" + "=" * 70)
    print("EVIDENCE FILTER")
    print("=" * 70)

    print(
        f"Total evidence items:     {total_evidence}"
    )

    print(
        f"Accepted evidence items:  {accepted_evidence}"
    )

    print(
        f"Rejected evidence items:  "
        f"{total_evidence - accepted_evidence}"
    )

    return filtered_data


def main():
    project_root = Path(__file__).resolve().parents[2]

    evidence_file = (
        project_root / "data" / "evidence.json"
    )

    evaluated_sources_file = (
        project_root
        / "data"
        / "evaluated_sources.json"
    )

    output_file = (
        project_root
        / "data"
        / "filtered_evidence.json"
    )

    evidence_data = load_json(evidence_file)

    evaluated_sources = load_json(
        evaluated_sources_file
    )

    filtered_data = filter_evidence(
        evidence_data,
        evaluated_sources,
    )

    output_file.write_text(
        json.dumps(
            filtered_data,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"\nSaved to: {output_file}"
    )


if __name__ == "__main__":
    main()