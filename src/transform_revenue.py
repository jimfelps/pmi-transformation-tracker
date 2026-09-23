from pathlib import Path
import warnings

import pandas as pd
from bs4 import XMLParsedAsHTMLWarning


warnings.filterwarnings(
    "ignore",
    category=XMLParsedAsHTMLWarning,
)


FILINGS_DIR = Path(
    "data/raw/filings"
)

OUTPUT_FILE = Path(
    "data/processed/quarterly_product_revenue.csv"
)


def find_revenue_table(file_path):
    """
    Find the PMI product-category revenue table.
    """

    tables = pd.read_html(file_path)

    for table in tables:

        table_text = (
            table
            .astype(str)
            .to_string()
        )

        if (
            "Total Smoke-free" in table_text
            and
            "Total PMI net revenues"
            in table_text
        ):
            return table

    raise ValueError(
        f"Revenue table not found in "
        f"{file_path.name}"
    )


def get_row_values(table, row_label):
    """
    Return numeric values from a selected
    revenue-table row.
    """

    row = table[
        table.iloc[:, 0]
        .astype(str)
        .str.strip()
        == row_label
    ]

    if row.empty:
        raise ValueError(
            f"Row not found: {row_label}"
        )

    values = []

    for value in row.iloc[0]:

        numeric_value = pd.to_numeric(
            value,
            errors="coerce",
        )

        if pd.notna(numeric_value):
            values.append(
                float(numeric_value)
            )

    return values

def remove_consecutive_duplicates(values):
    """
    Remove consecutive duplicate values
    created by SEC HTML table formatting.
    """

    cleaned_values = []

    for value in values:

        if (
            not cleaned_values
            or value != cleaned_values[-1]
        ):
            cleaned_values.append(value)

    return cleaned_values

def parse_2025_q1(file_path):

    table = find_revenue_table(file_path)

    smoke_free_values = remove_consecutive_duplicates(
        get_row_values(
            table,
            "Total Smoke-free",
        )
    )

    combustible_values = remove_consecutive_duplicates(
        get_row_values(
            table,
            "Total Combustible tobacco",
        )
    )

    total_values = remove_consecutive_duplicates(
        get_row_values(
            table,
            "Total PMI net revenues",
        )
    )

    return [
        {
            "year": 2025,
            "quarter": "Q1",
            "period_label": "2025-Q1",
            "product_name": "smoke_free",
            "revenue": smoke_free_values[0],
            "source_type": "SEC filing",
            "source_document": file_path.name,
            "derived": False,
        },
        {
            "year": 2025,
            "quarter": "Q1",
            "period_label": "2025-Q1",
            "product_name": "combustible",
            "revenue": combustible_values[0],
            "source_type": "SEC filing",
            "source_document": file_path.name,
            "derived": False,
        },
        {
            "year": 2025,
            "quarter": "Q1",
            "period_label": "2025-Q1",
            "product_name": "total",
            "revenue": total_values[0],
            "source_type": "SEC filing",
            "source_document": file_path.name,
            "derived": False,
        },
    ]

def parse_2025_ytd_quarter(
    file_path,
    quarter,
):

    table = find_revenue_table(file_path)

    smoke_free_values = remove_consecutive_duplicates(
        get_row_values(
            table,
            "Total Smoke-free",
        )
    )

    combustible_values = remove_consecutive_duplicates(
        get_row_values(
            table,
            "Total Combustible tobacco",
        )
    )

    total_values = remove_consecutive_duplicates(
        get_row_values(
            table,
            "Total PMI net revenues",
        )
    )

    records = []

    for product_name, values in [
        ("smoke_free", smoke_free_values),
        ("combustible", combustible_values),
        ("total", total_values),
    ]:

        records.append(
            {
                "year": 2025,
                "quarter": quarter,
                "period_label":
                    f"2025-{quarter}",
                "product_name":
                    product_name,
                "revenue":
                    values[2],
                "source_type":
                    "SEC filing",
                "source_document":
                    file_path.name,
                "derived":
                    False,
            }
        )

    return records

def parse_2025_annual(file_path):

    table = find_revenue_table(file_path)

    smoke_free_values = (
        remove_consecutive_duplicates(
            get_row_values(
                table,
                "Total Smoke-free",
            )
        )
    )

    combustible_values = (
        remove_consecutive_duplicates(
            get_row_values(
                table,
                "Total combustible tobacco products",
            )
        )
    )

    total_values = (
        remove_consecutive_duplicates(
            get_row_values(
                table,
                "Total PMI net revenues",
            )
        )
    )

    return {
        "smoke_free": smoke_free_values[0],
        "combustible": combustible_values[0],
        "total": total_values[0],
    }

def derive_2025_q4(
    quarterly_records,
    annual_values,
):

    q4_records = []

    for product_name in [
        "smoke_free",
        "combustible",
        "total",
    ]:

        q1_q3_total = sum(
            record["revenue"]
            for record in quarterly_records
            if (
                record["year"] == 2025
                and record["quarter"]
                in ["Q1", "Q2", "Q3"]
                and record["product_name"]
                == product_name
            )
        )

        q4_value = (
            annual_values[product_name]
            - q1_q3_total
        )

        q4_records.append(
            {
                "year": 2025,
                "quarter": "Q4",
                "period_label": "2025-Q4",
                "product_name":
                    product_name,
                "revenue": q4_value,
                "source_type":
                    "SEC filing",
                "source_document":
                    "2025-FY.html",
                "derived":
                    True,
            }
        )

    return q4_records

def parse_q1(file_path):
    """
    Parse standalone Q1 product revenue.
    """

    table = find_revenue_table(
        file_path
    )

    smoke_free_values = get_row_values(
        table,
        "Total Smoke-free",
    )

    combustible_values = get_row_values(
        table,
        "Total Combustible tobacco",
    )

    total_values = get_row_values(
        table,
        "Total PMI net revenues",
    )

    return [
        {
            "year": 2026,
            "quarter": "Q1",
            "period_label": "2026-Q1",
            "product_name": "smoke_free",
            "revenue": smoke_free_values[0],
            "source_type": "SEC filing",
            "source_document": file_path.name,
            "derived": False,
        },
        {
            "year": 2026,
            "quarter": "Q1",
            "period_label": "2026-Q1",
            "product_name": "combustible",
            "revenue": combustible_values[0],
            "source_type": "SEC filing",
            "source_document": file_path.name,
            "derived": False,
        },
        {
            "year": 2026,
            "quarter": "Q1",
            "period_label": "2026-Q1",
            "product_name": "total",
            "revenue": total_values[0],
            "source_type": "SEC filing",
            "source_document": file_path.name,
            "derived": False,
        },
    ]


def parse_q2(file_path):
    """
    Parse standalone Q2 product revenue.

    The Q2 filing contains both six-month
    YTD and standalone three-month values.
    The final pair of values represents Q2.
    """

    table = find_revenue_table(
        file_path
    )

    smoke_free_values = (
        remove_consecutive_duplicates(
            get_row_values(
                table,
                "Total Smoke-free",
            )
        )
    )

    combustible_values = (
        remove_consecutive_duplicates(
            get_row_values(
                table,
                "Total Combustible tobacco",
            )
        )
    )

    total_values = (
        remove_consecutive_duplicates(
            get_row_values(
                table,
                "Total PMI net revenues",
            )
        )
    )

    print(
        "Smoke-free values:",
        smoke_free_values,
    )

    print(
        "Combustible values:",
        combustible_values,
    )

    print(
        "Total values:",
        total_values,
    )

    return [
        {
            "year": 2026,
            "quarter": "Q2",
            "period_label": "2026-Q2",
            "product_name": "smoke_free",
            "revenue": smoke_free_values[2],
            "source_type": "SEC filing",
            "source_document": file_path.name,
            "derived": False,
        },
        {
            "year": 2026,
            "quarter": "Q2",
            "period_label": "2026-Q2",
            "product_name": "combustible",
            "revenue": combustible_values[2],
            "source_type": "SEC filing",
            "source_document": file_path.name,
            "derived": False,
        },
        {
            "year": 2026,
            "quarter": "Q2",
            "period_label": "2026-Q2",
            "product_name": "total",
            "revenue": total_values[2],
            "source_type": "SEC filing",
            "source_document": file_path.name,
            "derived": False,
        },
    ]


def validate_revenue(df):
    """
    Confirm product-category revenue
    reconciles to total PMI revenue.
    """

    for period_label, period in df.groupby(
        "period_label"
    ):

        values = (
            period
            .set_index("product_name")[
                "revenue"
            ]
        )

        calculated_total = (
            values["smoke_free"]
            + values["combustible"]
        )

        reported_total = values["total"]

        difference = (
            calculated_total
            - reported_total
        )

        print(
            f"{period_label}: "
            f"SFP + combustible = "
            f"{calculated_total:,.0f}; "
            f"reported total = "
            f"{reported_total:,.0f}; "
            f"difference = "
            f"{difference:,.0f}"
        )

        if abs(difference) > 1:
            raise ValueError(
                f"Revenue validation failed "
                f"for {period_label}"
            )


def main():

    records = []

        # 2025 quarterly revenue
    records.extend(
        parse_2025_q1(
            FILINGS_DIR / "2025-Q1.html"
        )
    )

    records.extend(
        parse_2025_ytd_quarter(
            FILINGS_DIR / "2025-Q2.html",
            "Q2",
        )
    )

    records.extend(
        parse_2025_ytd_quarter(
            FILINGS_DIR / "2025-Q3.html",
            "Q3",
        )
    )

    # Derived 2025 Q4
    annual_2025 = parse_2025_annual(
        FILINGS_DIR / "2025-FY.html"
    )

    records.extend(
        derive_2025_q4(
            records,
            annual_2025,
        )
    )

    # 2026 revenue
    records.extend(
        parse_q1(
            FILINGS_DIR / "2026-Q1.html"
        )
    )

    records.extend(
        parse_q2(
            FILINGS_DIR / "2026-Q2.html"
        )
    )

    result = pd.DataFrame(records)

    validate_revenue(result)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print("Quarterly Product Revenue")
    print("=" * 90)

    print(
        result.to_string(
            index=False
        )
    )

    print()
    print(
        f"Saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()