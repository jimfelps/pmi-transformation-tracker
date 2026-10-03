from pathlib import Path

import pandas as pd


ADJUSTMENTS_FILE = Path("data/raw/eps_adjustments.csv")
ADJUSTED_EPS_FILE = Path("data/raw/adjusted_eps.csv")
FINANCIALS_FILE = Path("data/processed/quarterly_financials.csv")
OUTPUT_FILE = Path("data/processed/quarterly_eps_adjustments.csv")


def load_data():
    adjustments = pd.read_csv(ADJUSTMENTS_FILE)
    adjusted_eps = pd.read_csv(ADJUSTED_EPS_FILE)
    financials = pd.read_csv(FINANCIALS_FILE)

    return adjustments, adjusted_eps, financials


def summarize_adjustments(adjustments):
    """
    Collapse individual EPS adjustments into one row per quarter.
    """

    summary = (
        adjustments
        .groupby(["year", "quarter"], as_index=False)
        .agg(
            total_eps_adjustment=("eps_impact", "sum"),
            adjustment_count=("adjustment", "count"),
        )
    )

    return summary


def build_quarterly_reconciliation(adjustments, financials):
    summary = summarize_adjustments(adjustments)

    financials = financials[
        [
            "year",
            "quarter",
            "diluted_eps",
        ]
    ].copy()

    result = financials.merge(
        summary,
        on=["year", "quarter"],
        how="left",
    )

    result["total_eps_adjustment"] = (
        result["total_eps_adjustment"].fillna(0)
    )

    result["adjustment_count"] = (
        result["adjustment_count"].fillna(0).astype(int)
    )

    result["adjusted_eps"] = (
        result["diluted_eps"]
        + result["total_eps_adjustment"]
    )

    return result


def main():
    adjustments, adjusted_eps, financials = load_data()

    result = build_quarterly_reconciliation(
        adjustments,
        financials,
    )

    result = result.merge(
        adjusted_eps.rename(
            columns={
                "adjusted_eps": "reported_adjusted_eps"
            }
        ),
        on=["year", "quarter"],
        how="left",
    )

    result["adjusted_eps_reconciliation"] = (
        result["adjusted_eps"]
        - result["reported_adjusted_eps"]
    )

    print()
    print("PMI Reported-to-Adjusted EPS")
    print("=" * 78)

    display = result[
        [
            "year",
            "quarter",
            "diluted_eps",
            "total_eps_adjustment",
            "adjusted_eps",
            "reported_adjusted_eps",
            "adjusted_eps_reconciliation",
            "adjustment_count",
        ]
    ].copy()

    print(
        display.to_string(
            index=False,
            formatters={
                "diluted_eps": lambda x: (
                    f"${x:.2f}" if pd.notna(x) else "N/A"
                ),
                "total_eps_adjustment": lambda x: f"${x:+.2f}",
                "adjusted_eps": lambda x: (
                    f"${x:.2f}" if pd.notna(x) else "N/A"
                ),
                "reported_adjusted_eps": lambda x: (
                    f"${x:.2f}" if pd.notna(x) else "N/A"
                ),
                "adjusted_eps_reconciliation": lambda x: (
                    f"${x:+.2f}" if pd.notna(x) else "N/A"
                ),
            },
        )
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
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()