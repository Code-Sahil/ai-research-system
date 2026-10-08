import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"


def load_filtered_evidence():
    file_path = DATA_DIR / "filtered_evidence.json"

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_filtered_evidence_file_exists():
    file_path = DATA_DIR / "filtered_evidence.json"

    assert file_path.exists(), "filtered_evidence.json does not exist"


def test_filtered_evidence_is_valid_json():
    data = load_filtered_evidence()

    assert isinstance(data, dict)
    assert data is not None


def test_filtered_evidence_is_not_empty():
    data = load_filtered_evidence()

    assert len(data) > 0
    assert len(data["subquestions"]) > 0


def test_subquestions_have_required_fields():
    data = load_filtered_evidence()

    for subquestion in data["subquestions"]:
        assert "question" in subquestion
        assert "sources" in subquestion

        assert isinstance(subquestion["question"], str)
        assert isinstance(subquestion["sources"], list)


def test_evidence_items_have_required_fields():
    data = load_filtered_evidence()

    for subquestion in data["subquestions"]:
        for source in subquestion["sources"]:
            assert "title" in source
            assert "evaluation" in source
            assert "evidence" in source

            for item in source["evidence"]:
                assert "claim" in item
                assert "evidence" in item
                assert "confidence" in item


def test_confidence_scores_are_valid():
    data = load_filtered_evidence()

    for subquestion in data["subquestions"]:
        for source in subquestion["sources"]:
            for item in source["evidence"]:
                confidence = item["confidence"]

                assert isinstance(confidence, (int, float))
                assert 0 <= confidence <= 1