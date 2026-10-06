import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "sources.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "source_text.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    )
}

MIN_TEXT_LENGTH = 500


def fetch_page(url: str) -> str | None:
    """Fetch a webpage and extract its main readable text."""

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # Remove elements that normally do not contain
        # useful research content.
        for element in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside",
                "form",
                "noscript",
            ]
        ):
            element.decompose()

        # Prefer the article itself when the website
        # provides a semantic <article> element.
        article = soup.find("article")

        if article:
            content = article
        else:
            content = soup.body

        if content is None:
            return None

        # Extract paragraph text rather than blindly
        # taking every piece of text on the page.
        paragraphs = content.find_all("p")

        if paragraphs:
            text = " ".join(
                paragraph.get_text(
                    " ",
                    strip=True,
                )
                for paragraph in paragraphs
            )
        else:
            text = content.get_text(
                " ",
                strip=True,
            )

        # Normalize whitespace.
        text = " ".join(text.split())

        if len(text) < MIN_TEXT_LENGTH:
            return None

        return text

    except requests.RequestException as error:
        print(f"Fetch failed: {error}")
        return None


def run_fetcher():
    """Fetch and clean all sources from sources.json."""

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
    successful_sources = 0
    failed_sources = 0

    for subquestion in data["subquestions"]:
        question = subquestion["question"]

        print("\n" + "=" * 70)
        print("Research sub-question:")
        print(question)

        fetched_sources = []

        for source in subquestion.get("sources", []):
            total_sources += 1

            title = source.get("title", "")
            url = source.get("url", "")

            print(f"\nFetching: {title}")
            print(f"URL: {url}")

            text = fetch_page(url)

            if text:
                successful_sources += 1

                print(
                    f"Success: {len(text):,} characters "
                    f"of usable text."
                )

                fetched_sources.append(
                    {
                        "title": title,
                        "url": url,
                        "text": text,
                    }
                )

            else:
                failed_sources += 1
                print(
                    "Failed: usable source text "
                    "could not be extracted."
                )

        output["subquestions"].append(
            {
                "question": question,
                "sources": fetched_sources,
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
    print("SOURCE FETCH SUMMARY")
    print("=" * 70)
    print(f"Total sources:      {total_sources}")
    print(f"Successfully read:  {successful_sources}")
    print(f"Failed:              {failed_sources}")
    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    run_fetcher()