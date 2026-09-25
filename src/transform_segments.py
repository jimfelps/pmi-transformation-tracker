from pathlib import Path
import warnings

import pandas as pd
from bs4 import XMLParsedAsHTMLWarning


warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

FILINGS_DIR = Path("data/raw/filings")
OUTPUT_FILE = Path("data/processed/quarterly_segment_profitability.csv")


SEGMENTS = {
    "International Smoke-Free": "international_smoke_free",
    "International Combustibles": "international_combustibles",
    "U.S.": "us",
    "Total": "total",
}


def find_segment_table(file_path, quarter):
    tables = pd.read_html(file_path)

    for table_number, table in enumerate(tables):
        table_text = table.to_string()

        required_terms = [
            "International Smoke-Free",
            "International Combustibles",
            "Net revenues",
            "Cost of sales",
            "Gross profit",
        ]

        if not all(
            term.lower() in table_text.lower()
            for term in required_terms
        ):
            continue

        if quarter == "Q2":
            if "Three Months Ended" not in table_text:
                continue

        print(f"Selected segment table: {table_number}")
        return table

    raise ValueError(
        f"Segment profitability table not found in {file_path}"
    )


def clean_numeric(value):
    if pd.isna(value):
        return None

    text = str(value).strip()

    if text in {"$", "", "nan"}:
        return None

    text = text.replace("$", "")
    text = text.replace(",", "")
    text = text.replace("(", "")
    text = text.replace(")", "")

    try:
        return float(text)
    except ValueError:
        return None


def get_row_values(table, row_name):
    values = []

    for _, row in table.iterrows():
        first_values = row.iloc[:3].tolist()

        if any(
            row_name.lower() == str(value).strip().lower()
            for value in first_values
        ):
            for value in row.iloc[3:]:
                numeric = clean_numeric(value)

                if numeric is not None:
                    values.append(numeric)

    if not values:
        raise ValueError(f"Row not found: {row_name}")

    return values


def remove_consecutive_duplicates(values):
    cleaned = []

    for value in values:
        if not cleaned or value != cleaned[-1]:
            cleaned.append(value)

    return cleaned


def parse_segment_table(file_path, current_year, quarter):
    table = find_segment_table(file_path, quarter)

    revenue_values = remove_consecutive_duplicates(
        get_row_values(table, "Net revenues")
    )

    cost_values = remove_consecutive_duplicates(
        get_row_values(table, "Cost of sales")
    )

    gross_profit_values = remove_consecutive_duplicates(
        get_row_values(table, "Gross profit")
    )

    print(f"\n{file_path.name}")
    print("Revenue:", revenue_values)
    print("Cost of sales:", cost_values)
    print("Gross profit:", gross_profit_values)

    if not (
        len(revenue_values) >= 8
        and len(cost_values) >= 8
        and len(gross_profit_values) >= 8
    ):
        raise ValueError(
            f"Unexpected segment table structure in {file_path.name}"
        )

    prior_year = current_year - 1

    records = []

    years = [current_year, prior_year]

    for year_index, year in enumerate(years):
        start = year_index * 4
        end = start + 4

        revenues = revenue_values[start:end]
        costs = cost_values[start:end]
        gross_profits = gross_profit_values[start:end]

        for segment_index, segment in enumerate(SEGMENTS.values()):
            revenue = revenues[segment_index]
            cost = costs[segment_index]
            gross_profit = gross_profits[segment_index]

            base_record = {
                "period_label": f"{year}-{quarter}",
                "segment": segment,
                "source_type": "SEC filing",
                "source_document": file_path.name,
            }

            records.append({
                **base_record,
                "metric": "revenue",
                "value": revenue,
                "derived": False,
            })

            records.append({
                **base_record,
                "metric": "cost_of_sales",
                "value": cost,
                "derived": False,
            })

            records.append({
                **base_record,
                "metric": "gross_profit",
                "value": gross_profit,
                "derived": False,
            })

            records.append({
                **base_record,
                "metric": "gross_margin",
                "value": gross_profit / revenue,
                "derived": True,
            })

    return records


def main():
    records = []

    records.extend(
        parse_segment_table(
            FILINGS_DIR / "2026-Q1.html",
            current_year=2026,
            quarter="Q1",
        )
    )

    records.extend(
        parse_segment_table(
            FILINGS_DIR / "2026-Q2.html",
            current_year=2026,
            quarter="Q2",
        )
    )

    result = pd.DataFrame(records)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False)

    print("\nNormalized segment profitability data:")
    print(result.to_string(index=False))

    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()