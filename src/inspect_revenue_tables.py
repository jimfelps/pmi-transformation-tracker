from pathlib import Path
import pandas as pd
import warnings
from bs4 import XMLParsedAsHTMLWarning


warnings.filterwarnings(
    "ignore",
    category=XMLParsedAsHTMLWarning,
)


FILINGS_DIR = Path(
    "data/raw/filings"
)


def inspect_file(file_path):

    print()
    print("=" * 100)
    print(file_path.name)
    print("=" * 100)

    tables = pd.read_html(file_path)

    print(
        f"Tables found: {len(tables)}"
    )

    for table_number, table in enumerate(
        tables
    ):

        table_text = (
            table
            .astype(str)
            .to_string()
        )

        if (
            "Total Smoke-free" in table_text
            and
            "Total PMI net revenues" in table_text
        ):

            print()
            print(
                f"TABLE {table_number}"
            )
            print("-" * 100)
            print(
                table.to_string(
                    index=False
                )
            )


def main():

    files = [
        FILINGS_DIR / "2025-Q1.html",
        FILINGS_DIR / "2025-Q2.html",
    ]

    for file_path in files:
        inspect_file(file_path)


if __name__ == "__main__":
    main()