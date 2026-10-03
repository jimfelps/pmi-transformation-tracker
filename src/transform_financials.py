import json
from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/raw/pmi_companyfacts.json")
OUTPUT_FILE = Path("data/processed/quarterly_financials.csv")


CONCEPTS = {
    "revenue": {
        "concept": "RevenueFromContractWithCustomerExcludingAssessedTax",
        "unit": "USD",
        "q4_method": "subtract",
    },
    "operating_income": {
        "concept": "OperatingIncomeLoss",
        "unit": "USD",
        "q4_method": "subtract",
    },
    "net_interest": {
        "concept": "InterestIncomeExpenseNonoperatingNet",
        "unit": "USD",
        "q4_method": "subtract",
    },
    "nonservice_benefit_expense": {
        "concept": "NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent",
        "unit": "USD",
        "q4_method": "subtract",
    },
    "pretax_before_equity_investments": {
        "concept": "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
        "unit": "USD",
        "q4_method": "subtract",
    },
    "income_tax_expense": {
        "concept": "IncomeTaxExpenseBenefit",
        "unit": "USD",
        "q4_method": "subtract",
    },
    "equity_method_income": {
        "concept": "IncomeLossFromEquityMethodInvestments",
        "unit": "USD",
        "q4_method": "subtract",
    },
    "consolidated_net_income": {
        "concept": "ProfitLoss",
        "unit": "USD",
        "q4_method": "subtract",
    },
    "noncontrolling_interest": {
        "concept": "NetIncomeLossAttributableToNoncontrollingInterest",
        "unit": "USD",
        "q4_method": "subtract",
    },
    "pmi_net_income": {
        "concept": "NetIncomeLoss",
        "unit": "USD",
        "q4_method": "subtract",
    },
    "common_net_income": {
        "concept": "NetIncomeLossAvailableToCommonStockholdersBasic",
        "unit": "USD",
        "q4_method": "subtract",
    },
    "diluted_eps": {
        "concept": "EarningsPerShareDiluted",
        "unit": "USD/shares",
        "q4_method": "none",
    },
    "diluted_shares": {
        "concept": "WeightedAverageNumberOfDilutedSharesOutstanding",
        "unit": "shares",
        "q4_method": "none",
    },
    "rbh_impairment": {
    "concept": "EquitySecuritiesWithoutReadilyDeterminableFairValueImpairmentLossAnnualAmount",
    "unit": "USD",
    "q4_method": "subtract",
    "missing_value": 0,
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


def add_derived_q4(df, missing_value=None):
    """Derive standalone Q4 from FY less Q1-Q3."""

    q4_records = []

    for year in sorted(df["year"].unique()):
        year_data = df[df["year"] == year]

        values = dict(
            zip(
                year_data["quarter"],
                year_data["value"],
            )
        )

        if "FY" not in values:
            continue

        if missing_value is not None:
            q1 = values.get("Q1", missing_value)
            q2 = values.get("Q2", missing_value)
            q3 = values.get("Q3", missing_value)
        else:
            required = {"Q1", "Q2", "Q3"}

            if not required.issubset(values):
                continue

            q1 = values["Q1"]
            q2 = values["Q2"]
            q3 = values["Q3"]

        q4_value = (
            values["FY"]
            - q1
            - q2
            - q3
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

    df = df[df["quarter"] != "FY"]

    return df


def transform_metric(data, metric_name, config):
    observations = get_observations(
        data,
        config["concept"],
        config["unit"],
    )

    df = get_standalone_quarters(observations)

    
    if config.get("q4_method") == "subtract":
        df = add_derived_q4(
            df,
            missing_value=config.get("missing_value"),
        )
    else:
        df = df[df["quarter"] != "FY"]

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

    result["rbh_impairment"] = (
        result["rbh_impairment"].fillna(0)
    )

    result["operating_margin"] = (
        result["operating_income"] / result["revenue"]
    )

    result["below_line_residual"] = (
    result["consolidated_net_income"]
    - (
        result["pretax_before_equity_investments"]
        - result["income_tax_expense"]
        - result["rbh_impairment"]
        + result["equity_method_income"]
    )
)

    result["nci_reconciliation_check"] = (
    result["consolidated_net_income"]
    - result["noncontrolling_interest"]
    - result["pmi_net_income"]
)

    result["common_income_adjustment"] = (
    result["common_net_income"]
    - result["pmi_net_income"]
)

    result["eps_reconciliation_check"] = (
    result["common_net_income"]
    / result["diluted_shares"]
    - result["diluted_eps"]
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