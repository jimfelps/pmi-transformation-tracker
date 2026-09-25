from pathlib import Path
import pandas as pd
import warnings
from bs4 import XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

FILINGS_DIR = Path("data/raw/filings")


def inspect_filing(file_path):
    print("\n" + "=" * 80)
    print(f"FILE: {file_path.name}")
    print("=" * 80)

    tables = pd.read_html(file_path)

    print(f"Tables found: {len(tables)}")

    search_terms = [
        "International Smoke-Free",
        "International Combustibles",
        "Gross Profit",
        "Cost of Sales",
    ]

    for i, table in enumerate(tables):
        table_text = table.to_string()

        if any(term.lower() in table_text.lower() for term in search_terms):
            print("\n" + "-" * 80)
            print(f"TABLE {i}")
            print("-" * 80)
            print(table.to_string(index=False))


def main():
    filing_files = [
        FILINGS_DIR / "2026-Q1.html",
    ]

    for file_path in filing_files:
        inspect_filing(file_path)


if __name__ == "__main__":
    main()