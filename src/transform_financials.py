import json
from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/raw/pmi_companyfacts.json")
OUTPUT_FILE = Path("data/processed/quarterly_financials.csv")


CONCEPTS = {
    "revenue": {
        "concept": "RevenueFromContractWithCustomerExcludingAssessedTax",
        "unit": "USD",
    },
    "operating_income": {
        "concept": "OperatingIncomeLoss",
        "unit": "USD",
    },
    "diluted_eps": {
        "concept": "EarningsPerShareDiluted",
        "unit": "USD/shares",
    },
}


def load_company_facts():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_observations(data, concept_name, unit):
    """Return SEC observations for one US-GAAP concept."""

    return data["facts"]["us-gaap"][concept_name]["units"][unit]


def get_standalone_quarters(observations, start_year=2024):
    """
    Extract standalone Q1-Q3 observations and annual observations.

    Q4 is derived later as:
        FY - Q1 - Q2 - Q3
    """

    records = []

    for obs in observations:
        if obs.get("form") not in ("10-Q", "10-K"):
            continue

        start = obs.get("start")
        end = obs.get("end")

        if not start or not end:
            continue

        calendar_year = int(end[:4])

        if calendar_year < start_year:
            continue

        start_month_day = start[5:]
        end_month_day = end[5:]

        quarter = None

        # PMI has a calendar fiscal year.
        if start_month_day == "01-01" and end_month_day == "03-31":
            quarter = "Q1"

        elif start_month_day == "04-01" and end_month_day == "06-30":
            quarter = "Q2"

        elif start_month_day == "07-01" and end_month_day == "09-30":
            quarter = "Q3"

        elif start_month_day == "01-01" and end_month_day == "12-31":
            quarter = "FY"

        if quarter is None:
            continue

        records.append(
            {
                "year": calendar_year,
                "quarter": quarter,
                "value": obs["val"],
                "filed": obs.get("filed"),
                "accession": obs.get("accn"),
            }
        )

    df = pd.DataFrame(records)

    # The SEC may contain the same historical fact in multiple later filings.
    # Keep the most recently filed version.
    df = (
        df.sort_values("filed")
        .drop_duplicates(
            subset=["year", "quarter"],
            keep="last",
        )
    )

    return df


def add_derived_q4(df):
    """Derive standalone Q4 from FY less Q1-Q3."""

    q4_records = []

    for year in sorted(df["year"].unique()):
        year_data = df[df["year"] == year]

        values = dict(zip(year_data["quarter"], year_data["value"]))

        required = {"Q1", "Q2", "Q3", "FY"}

        if required.issubset(values):
            q4_value = (
                values["FY"]
                - values["Q1"]
                - values["Q2"]
                - values["Q3"]
            )

            q4_records.append(
                {
                    "year": year,
                    "quarter": "Q4",
                    "value": q4_value,
                    "filed": None,
                    "accession": None,
                }
            )

    if q4_records:
        df = pd.concat(
            [df, pd.DataFrame(q4_records)],
            ignore_index=True,
        )

    # We only want standalone quarters in the final dataset.
    df = df[df["quarter"] != "FY"]

    return df


def transform_metric(data, metric_name, config):
    observations = get_observations(
        data,
        config["concept"],
        config["unit"],
    )

    df = get_standalone_quarters(observations)
    df = add_derived_q4(df)

    df = df.rename(columns={"value": metric_name})

    return df[["year", "quarter", metric_name]]


def main():
    data = load_company_facts()

    metric_frames = []

    for metric_name, config in CONCEPTS.items():
        metric_df = transform_metric(
            data,
            metric_name,
            config,
        )

        metric_frames.append(metric_df)

    result = metric_frames[0]

    for metric_df in metric_frames[1:]:
        result = result.merge(
            metric_df,
            on=["year", "quarter"],
            how="outer",
        )

    result["operating_margin"] = (
        result["operating_income"] / result["revenue"]
    )

    quarter_order = {
        "Q1": 1,
        "Q2": 2,
        "Q3": 3,
        "Q4": 4,
    }

    result["quarter_num"] = result["quarter"].map(quarter_order)

    result = (
        result.sort_values(["year", "quarter_num"])
        .drop(columns="quarter_num")
        .reset_index(drop=True)
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    result["source_type"] = "SEC Company Facts"
    result["source_document"] = "pmi_companyfacts.json"

    result["derived"] = (
    result["quarter"] == "Q4"
    )

    result.to_csv(OUTPUT_FILE, index=False)

    # Friendly terminal display.
    display = result.copy()

    display["revenue"] = display["revenue"] / 1_000_000_000
    display["operating_income"] = (
        display["operating_income"] / 1_000_000_000
    )

    display["operating_margin"] = (
        display["operating_margin"] * 100
    )

    print()
    print("PMI Quarterly Financials")
    print("=" * 75)

    print(
        display.to_string(
            index=False,
            formatters={
                "revenue": lambda x: f"${x:,.3f}B",
                "operating_income": lambda x: f"${x:,.3f}B",
                "diluted_eps": lambda x: f"${x:,.2f}",
                "operating_margin": lambda x: f"{x:.1f}%",
            },
        )
    )

    print()
    print(f"Processed data saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()