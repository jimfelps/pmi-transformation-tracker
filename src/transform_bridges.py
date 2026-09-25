from pathlib import Path
import warnings

import pandas as pd
from bs4 import XMLParsedAsHTMLWarning


warnings.filterwarnings(
    "ignore",
    category=XMLParsedAsHTMLWarning,
)

FILINGS_DIR = Path("data/raw/filings")

OUTPUT_FILE = Path(
    "data/processed/quarterly_segment_bridges.csv"
)


SEGMENTS = {
    "international_smoke_free": "international_smoke_free",
    "international_combustibles": "international_combustibles",
}


def clean_numeric(value):
    if pd.isna(value):
        return None

    text = str(value).strip()

    if text in {
        "",
        "$",
        "—",
        "-",
        "nan",
    }:
        return 0.0 if text in {"—", "-"} else None

    negative = (
        text.startswith("(")
        and text.endswith(")")
    )

    text = (
        text.replace("$", "")
        .replace(",", "")
        .replace("(", "")
        .replace(")", "")
        .strip()
    )

    try:
        number = float(text)

        if negative:
            number = -number

        return number

    except ValueError:
        return None


def find_bridge_tables(file_path, quarter):
    tables = pd.read_html(file_path)

    candidates = []

    for table_number, table in enumerate(tables):
        table_text = table.to_string().lower()

        required_terms = [
            "financial summary",
            "net revenues",
            "gross profit",
            "price",
        ]

        if not all(
            term in table_text
            for term in required_terms
        ):
            continue

        # Q2 filings contain both quarterly
        # and six-month YTD bridge tables.
        if quarter == "Q2":
            if "quarters ended" not in table_text:
                continue

            if "six months ended" in table_text:
                continue

        candidates.append(
            (table_number, table)
        )

    return candidates


def get_metric_row(table, metric_name):
    for _, row in table.iterrows():
        first_values = row.iloc[:3].tolist()

        if any(
            metric_name.lower()
            == str(value).strip().lower()
            for value in first_values
        ):
            return row

    raise ValueError(
        f"Metric row not found: {metric_name}"
    )


def extract_bridge_values(row, quarter):
    if quarter == "Q1":
        column_groups = {
            "total_change": [24, 25, 26],
            "currency": [27, 28, 29],
            "price": [30, 31, 32],
            "volume_mix_other": [33, 34, 35],
            "cost": [36, 37, 38],
        }

    elif quarter == "Q2":
        column_groups = {
            "total_change": [24, 25, 26],
            "currency": [27, 28, 29],
            "acquisitions_divestitures": [30, 31, 32],
            "price": [33, 34, 35],
            "volume_mix_other": [36, 37, 38],
            "cost": [39, 40, 41],
        }

    else:
        raise ValueError(
            f"Unsupported quarter: {quarter}"
        )

    result = {}

    for driver, columns in column_groups.items():
        value = None

        for column in columns:
            if column >= len(row):
                continue

            numeric = clean_numeric(
                row.iloc[column]
            )

            if numeric is not None:
                value = numeric
                break

        result[driver] = value

    return result


def identify_segment(
    revenue_row,
    period_label,
):
    """
    Identify the reportable segment using the
    current-period revenue reported in the bridge.

    These values are validated against the segment
    profitability data extracted separately.
    """

    current_revenue = None

    # Current-period revenue appears near the
    # beginning of the bridge row.
    for column in range(3, min(15, len(revenue_row))):
        numeric = clean_numeric(
            revenue_row.iloc[column]
        )

        if numeric is not None:
            current_revenue = numeric
            break

    expected_revenue = {
        "2026-Q1": {
            3836.0: "international_smoke_free",
            5688.0: "international_combustibles",
        },
        "2026-Q2": {
            3877.0: "international_smoke_free",
            6459.0: "international_combustibles",
        },
    }

    return expected_revenue.get(
        period_label,
        {}
    ).get(current_revenue)


def parse_filing(
    file_path,
    period_label,
    quarter,
):
    candidates = find_bridge_tables(
        file_path,
        quarter,
    )

    records = []

    print(
        f"\n{file_path.name}: "
        f"{len(candidates)} bridge candidates"
    )

    for table_number, table in candidates:
        revenue_row = get_metric_row(
            table,
            "Net Revenues",
        )

        gross_profit_row = get_metric_row(
            table,
            "Gross Profit",
        )

        revenue_values = extract_bridge_values(
            revenue_row,
            quarter,
        )

        gross_profit_values = extract_bridge_values(
            gross_profit_row,
            quarter,
        )

        segment = identify_segment(
            revenue_row,
            period_label,
        )

        if segment is None:
            continue

        print(
            f"Table {table_number}: {segment}"
        )
        print(
            "  Revenue:",
            revenue_values,
        )
        print(
            "  Gross Profit:",
            gross_profit_values,
        )

        for metric_name, values in [
            (
                "revenue_change",
                revenue_values,
            ),
            (
                "gross_profit_change",
                gross_profit_values,
            ),
        ]:

            for driver, value in values.items():

                if value is None:
                    continue

                records.append(
                    {
                        "period_label": period_label,
                        "segment": segment,
                        "metric": metric_name,
                        "driver": driver,
                        "value": value,
                        "source_type": "SEC filing",
                        "source_document": file_path.name,
                        "derived": False,
                    }
                )

    return records

def validate_bridges(result):
    print("\nBridge validation")
    print("=" * 80)

    for (
        period_label,
        segment,
        metric,
    ), group in result.groupby(
        [
            "period_label",
            "segment",
            "metric",
        ]
    ):
        total_change = group.loc[
            group["driver"] == "total_change",
            "value",
        ].iloc[0]

        driver_total = group.loc[
            group["driver"] != "total_change",
            "value",
        ].sum()

        difference = (
            total_change
            - driver_total
        )

        print(
            f"{period_label} | "
            f"{segment} | "
            f"{metric}: "
            f"reported={total_change:.1f}, "
            f"drivers={driver_total:.1f}, "
            f"difference={difference:.1f}"
        )

        if abs(difference) > 2:
            raise ValueError(
                "Bridge does not reconcile: "
                f"{period_label}, "
                f"{segment}, "
                f"{metric}"
            )

def main():
    records = []

    records.extend(
        parse_filing(
            FILINGS_DIR / "2026-Q1.html",
            "2026-Q1",
            "Q1",
        )
    )

    records.extend(
        parse_filing(
            FILINGS_DIR / "2026-Q2.html",
            "2026-Q2",
            "Q2",
        )
    )

    result = pd.DataFrame(records)

    validate_bridges(result)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nNormalized bridge data:")
    print(
        result.to_string(
            index=False
        )
    )

    print(
        f"\nSaved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()