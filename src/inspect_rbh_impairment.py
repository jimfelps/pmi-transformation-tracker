from pathlib import Path

from bs4 import BeautifulSoup


FILINGS_DIR = Path("data/raw/filings")

FILES = [
    "2024-FY.html",
    "2026-Q2.html",
]

SEARCH_LABEL = "Impairment related to the RBH equity investment"


def inspect_filing(filename):
    path = FILINGS_DIR / filename

    print()
    print("=" * 100)
    print(filename)
    print("=" * 100)

    html = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    matches = []

    for row in soup.find_all("tr"):
        row_text = row.get_text(
            separator=" ",
            strip=True,
        )

        if SEARCH_LABEL.lower() in row_text.lower():
            matches.append(row)

    if not matches:
        print(f"'{SEARCH_LABEL}' not found in a table row.")
        return

    print(f"Found {len(matches)} matching row(s).")

    for i, row in enumerate(matches, start=1):
        print()
        print(f"MATCH {i}")
        print("-" * 100)

        print("VISIBLE TEXT:")
        print(
            row.get_text(
                separator=" | ",
                strip=True,
            )
        )

        print()
        print("HTML:")
        print(row.prettify())


def main():
    for filename in FILES:
        inspect_filing(filename)


if __name__ == "__main__":
    main()