from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/processed/quarterly_financials.csv")
OUTPUT_FILE = Path("data/processed/earnings_bridge.csv")


def load_financials():
    return pd.read_csv(INPUT_FILE)


def get_quarter(df, year, quarter):
    row = df[
        (df["year"] == year)
        & (df["quarter"] == quarter)
    ]

    if len(row) != 1:
        raise ValueError(
            f"Expected one row for {year} {quarter}, "
            f"found {len(row)}."
        )

    return row.iloc[0]


def build_bridge(
    prior,
    current,
    prior_period,
    current_period,
):
    """
    Build a period-over-period bridge from operating income
    to PMI-attributable net income.

    Positive bridge values increase PMI net income.
    Negative bridge values decrease PMI net income.
    """

    bridge = [
        {
            "sort_order": 1,
            "component": "Operating Income",
            "prior_value": prior["operating_income"],
            "current_value": current["operating_income"],
            "bridge_value": (
                current["operating_income"]
                - prior["operating_income"]
            ),
        },
        {
            "sort_order": 2,
            "component": "Net Interest",
            "prior_value": prior["net_interest"],
            "current_value": current["net_interest"],
            "bridge_value": (
                current["net_interest"]
                - prior["net_interest"]
            ),
        },
        {
            "sort_order": 3,
            "component": "Non-Service Benefits",
            "prior_value": prior["nonservice_benefit_expense"],
            "current_value": current["nonservice_benefit_expense"],
            "bridge_value": -(
                current["nonservice_benefit_expense"]
                - prior["nonservice_benefit_expense"]
            ),
        },
        {
            "sort_order": 4,
            "component": "Income Taxes",
            "prior_value": prior["income_tax_expense"],
            "current_value": current["income_tax_expense"],
            "bridge_value": -(
                current["income_tax_expense"]
                - prior["income_tax_expense"]
            ),
        },
        {
            "sort_order": 5,
            "component": "Equity Investments",
            "prior_value": prior["equity_method_income"],
            "current_value": current["equity_method_income"],
            "bridge_value": (
                current["equity_method_income"]
                - prior["equity_method_income"]
            ),
        },
        {
            "sort_order": 6,
            "component": "RBH Impairment",
            "prior_value": prior["rbh_impairment"],
            "current_value": current["rbh_impairment"],
            "bridge_value": -(
                current["rbh_impairment"]
                - prior["rbh_impairment"]
            ),
        },
        {
            "sort_order": 7,
            "component": "Noncontrolling Interest",
            "prior_value": prior["noncontrolling_interest"],
            "current_value": current["noncontrolling_interest"],
            "bridge_value": -(
                current["noncontrolling_interest"]
                - prior["noncontrolling_interest"]
            ),
        },
    ]

    result = pd.DataFrame(bridge)

    result["prior_period"] = prior_period
    result["current_period"] = current_period

    return result


def main():
    df = load_financials()

    prior_period = "2025 Q2"
    current_period = "2026 Q2"

    prior = get_quarter(df, 2025, "Q2")
    current = get_quarter(df, 2026, "Q2")

    bridge = build_bridge(
        prior,
        current,
        prior_period,
        current_period,
    )

    bridge_total = bridge["bridge_value"].sum()

    actual_change = (
        current["pmi_net_income"]
        - prior["pmi_net_income"]
    )

    reconciliation_check = bridge_total - actual_change

    print()
    print("PMI Earnings Bridge")
    print("=" * 70)
    print(f"{prior_period} → {current_period}")
    print()

    display = bridge[
        ["component", "bridge_value"]
    ].copy()

    display["bridge_value"] = (
        display["bridge_value"] / 1_000_000
    )

    print(
        display.to_string(
            index=False,
            formatters={
                "bridge_value": lambda x: f"${x:+,.0f}M"
            },
        )
    )

    print()
    print("-" * 70)

    print(
        "Bridge total:       "
        f"${bridge_total / 1_000_000:+,.0f}M"
    )

    print(
        "Actual PMI change:  "
        f"${actual_change / 1_000_000:+,.0f}M"
    )

    print(
        "Reconciliation:     "
        f"${reconciliation_check / 1_000_000:+,.0f}M"
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    bridge.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()