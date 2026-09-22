from pathlib import Path
import warnings

import pandas as pd
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning


FILINGS_DIR = Path("data/raw/filings")
OUTPUT_FILE = Path("data/processed/quarterly_shipments.csv")


warnings.filterwarnings(
    "ignore",
    category=XMLParsedAsHTMLWarning,
)


METRIC_MAP = {
    "Total PMI": "total",
    "Total": "total",
    "SFP": "smoke_free",
    "Smoke-Free Products": "smoke_free",
    "Smoke-Free Products (1)": "smoke_free",
    "HTU": "htu",
    "Oral SFP": "oral_sfp",
    "E-vapor": "e_vapor",
    "Cigarettes": "cigarettes",
}


def clean_text(text):
    """Collapse repeated whitespace."""
    return " ".join(text.split())


def clean_cells(row):
    """Remove blank cells created by SEC HTML formatting."""
    return [
        cell
        for cell in row
        if cell != ""
    ]


def table_to_rows(table):
    """Convert an HTML table into cleaned rows."""

    rows = []

    for tr in table.find_all("tr"):
        cells = [
            clean_text(cell.get_text(" ", strip=True))
            for cell in tr.find_all(["th", "td"])
        ]

        cells = clean_cells(cells)

        if cells:
            rows.append(cells)

    return rows


def find_shipment_tables(file_path):
    """
    Find standardized equivalent-unit shipment tables.
    """

    html = file_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    soup = BeautifulSoup(html, "lxml")

    matches = []

    for table in soup.find_all("table"):

        text = clean_text(
            table.get_text(" ", strip=True)
        ).lower()

        required_terms = [
            "shipment volume",
            "cigarettes",
            "htu",
            "oral sfp",
            "e-vapor",
        ]

        if all(term in text for term in required_terms):
            matches.append(table)

    return matches


def is_quarterly_table(rows, quarter):
    """
    Determine whether a table represents a standalone quarter
    rather than a year-to-date period.
    """

    text = " ".join(
        " ".join(row)
        for row in rows
    ).lower()

    if quarter == "Q1":
        # Q1 YTD and standalone quarter are the same period,
        # so any standardized shipment table is acceptable.
        return True

    if quarter == "Q2":
        return (
            "quarters ended june 30" in text
            or "three months ended june 30" in text
        )

    if quarter == "Q3":
        return (
            "quarters ended september 30" in text
            or "three months ended september 30" in text
        )

    return False


def parse_2025_table(rows):
    """
    Parse 2025-style tables where metrics are columns.

    Example:
    Total PMI | SFP | HTU | Oral SFP | E-vapor | Cigarettes
    200.1     | 44.8| 38.8| 5.2      | 0.9     | 155.2
    """

    header = None
    values = None

    for row in rows:

        if (
            "Total PMI" in row
            and "Cigarettes" in row
        ):
            header = row

        if (
            row
            and row[0].startswith(
                "Total Shipment Volume"
            )
        ):
            values = row[1:]

    if header is None or values is None:
        return None

    result = {}

    for metric_name, value in zip(
        header,
        values,
    ):
        canonical_name = METRIC_MAP.get(
            metric_name
        )

        if canonical_name:
            result[canonical_name] = float(value)

    return result


def parse_2026_table(rows):
    """
    Parse 2026-style tables where metrics are rows.

    Example:
    Total               | 205.2 | 200.1 | 2.5 | %
    Cigarettes          | 156.9 | 155.2 | 1.1 | %
    Smoke-Free Products | 48.2  | 44.8  | 7.5 | %
    """

    result = {}

    for row in rows:

        if len(row) < 2:
            continue

        metric_name = row[0]

        canonical_name = METRIC_MAP.get(
            metric_name
        )

        if canonical_name is None:
            continue

        try:
            current_value = float(row[1])
        except ValueError:
            continue

        result[canonical_name] = current_value

    if not result:
        return None

    return result


def parse_filing(file_path):
    """
    Extract standalone quarterly shipment metrics
    from one filing.
    """

    period = file_path.stem

    year_text, quarter = period.split("-")
    year = int(year_text)

    tables = find_shipment_tables(file_path)

    for table in tables:

        rows = table_to_rows(table)

        if not is_quarterly_table(
            rows,
            quarter,
        ):
            continue

        if year == 2025:
            metrics = parse_2025_table(rows)

        elif year >= 2026:
            metrics = parse_2026_table(rows)

        else:
            metrics = None

        if metrics:
            return {
                "year": year,
                "quarter": quarter,
                **metrics,
            }

    return None


def validate_shipments(df):
    """
    Check that component shipment volumes reconcile
    to reported totals.
    """

    print()
    print("Validation")
    print("=" * 80)

    for _, row in df.iterrows():

        smoke_free_components = (
            row["htu"]
            + row["oral_sfp"]
            + row["e_vapor"]
        )

        total_components = (
            row["cigarettes"]
            + row["smoke_free"]
        )

        smoke_free_difference = (
            row["smoke_free"]
            - smoke_free_components
        )

        total_difference = (
            row["total"]
            - total_components
        )

        print(
            f"{row['year']} {row['quarter']} | "
            f"SFP diff: {smoke_free_difference:+.2f} | "
            f"Total diff: {total_difference:+.2f}"
        )


def main():

    filing_files = (
        sorted(FILINGS_DIR.glob("2025-*.html"))
        + sorted(FILINGS_DIR.glob("2026-*.html"))
    )

    records = []

    for file_path in filing_files:

        record = parse_filing(file_path)

        if record:
            records.append(record)
        else:
            print(
                f"WARNING: No quarterly shipment "
                f"data extracted from {file_path.stem}"
            )

    result = pd.DataFrame(records)

    quarter_order = {
        "Q1": 1,
        "Q2": 2,
        "Q3": 3,
        "Q4": 4,
    }

    result["quarter_num"] = (
        result["quarter"].map(quarter_order)
    )

    result = (
        result
        .sort_values(
            ["year", "quarter_num"]
        )
        .drop(columns="quarter_num")
        .reset_index(drop=True)
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print("PMI Quarterly Shipment Volume")
    print("=" * 80)

    print(
        result.to_string(
            index=False
        )
    )

    validate_shipments(result)

    print()
    print(
        f"Processed data saved to: "
        f"{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()