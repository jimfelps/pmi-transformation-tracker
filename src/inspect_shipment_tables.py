from pathlib import Path

from bs4 import BeautifulSoup


FILINGS_DIR = Path("data/raw/filings")

SEARCH_TERMS = [
    "shipment volume",
    "cigarettes",
    "heated tobacco",
    "htu",
    "oral sfp",
    "e-vapor",
    "smoke-free",
]


def clean_text(text):
    """Collapse whitespace to make SEC table text easier to inspect."""
    return " ".join(text.split())


def inspect_filing(file_path):
    print()
    print("=" * 100)
    print(f"FILING: {file_path.stem}")
    print("=" * 100)

    html = file_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    soup = BeautifulSoup(html, "lxml")

    tables = soup.find_all("table")

    print(f"Tables found: {len(tables):,}")

    matches = []

    for table_number, table in enumerate(tables, start=1):
        table_text = clean_text(
            table.get_text(" ", strip=True)
        )

        table_text_lower = table_text.lower()

        matched_terms = [
            term
            for term in SEARCH_TERMS
            if term in table_text_lower
        ]

        # Require at least two relevant terms so we don't print
        # every random table that happens to mention cigarettes.
        if len(matched_terms) >= 2:
            matches.append(
                (
                    table_number,
                    matched_terms,
                    table_text,
                )
            )

    print(f"Potential shipment tables: {len(matches)}")

    for table_number, matched_terms, table_text in matches:
        print()
        print("-" * 100)
        print(f"TABLE #{table_number}")
        print(f"MATCHED TERMS: {', '.join(matched_terms)}")
        print("-" * 100)

        # Limit terminal output so giant SEC tables don't overwhelm us.
        print(table_text[:3000])

        if len(table_text) > 3000:
            print()
            print("[TABLE TEXT TRUNCATED]")


def main():
    filing_files = sorted(
        FILINGS_DIR.glob("*.html")
    )

    if not filing_files:
        print("No filing files found.")
        return

    print(
        f"Inspecting {len(filing_files)} PMI filings "
        f"in {FILINGS_DIR}..."
    )

    for file_path in filing_files:
        inspect_filing(file_path)


if __name__ == "__main__":
    main()