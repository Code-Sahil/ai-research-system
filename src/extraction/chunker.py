import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "source_text.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "source_chunks.json"

CHUNK_SIZE = 6000
OVERLAP = 500


def chunk_text(text: str) -> list[str]:
    """Split source text into overlapping chunks."""

    if not text:
        return []

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - OVERLAP

    return chunks


def run_chunker():
    """Create chunks for every fetched source."""

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    output = {
        "question": data["question"],
        "subquestions": [],
    }

    total_sources = 0
    total_chunks = 0

    for subquestion in data["subquestions"]:
        question = subquestion["question"]

        chunked_sources = []

        for source in subquestion.get("sources", []):
            total_sources += 1

            text = source.get("text", "")

            chunks = chunk_text(text)

            total_chunks += len(chunks)

            chunked_sources.append(
                {
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "chunks": chunks,
                }
            )

            print(
                f"\n{source.get('title', '')}"
            )
            print(
                f"  Source length: {len(text):,} characters"
            )
            print(
                f"  Chunks: {len(chunks)}"
            )

        output["subquestions"].append(
            {
                "question": question,
                "sources": chunked_sources,
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
    print("CHUNKING SUMMARY")
    print("=" * 70)
    print(f"Sources processed: {total_sources}")
    print(f"Total chunks:      {total_chunks}")
    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_chunker()