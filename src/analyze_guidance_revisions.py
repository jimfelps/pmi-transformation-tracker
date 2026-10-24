
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = BASE_DIR / "data" / "analysis"

INPUT_FILE = ANALYSIS_DIR / "guidance_accuracy.csv"
OUTPUT_FILE = ANALYSIS_DIR / "guidance_revisions.csv"


def main():
    guidance = pd.read_csv(
        INPUT_FILE,
        parse_dates=["event_date"],
    )

    required_columns = [
        "fiscal_year",
        "event_date",
        "event_type",
        "reported_midpoint",
        "adjusted_midpoint",
        "currency_neutral_midpoint",
        "adjustments",
        "currency_impact_forecast",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in guidance.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Order guidance events chronologically within each year.
    guidance = guidance.sort_values(
        ["fiscal_year", "event_date"]
    ).copy()

    # Track the immediately preceding disclosure.
    guidance["previous_event_date"] = (
        guidance.groupby("fiscal_year")["event_date"]
        .shift(1)
    )

    metrics = [
        "reported_midpoint",
        "adjusted_midpoint",
        "currency_neutral_midpoint",
        "adjustments",
        "currency_impact_forecast",
    ]

    # Calculate revisions within each fiscal year.
    for metric in metrics:
        previous = (
            guidance.groupby("fiscal_year")[metric]
            .shift(1)
        )

        guidance[f"previous_{metric}"] = previous
        guidance[f"change_{metric}"] = (
            guidance[metric] - previous
        )

    # Initial guidance is a baseline, not a revision.
    revisions = guidance[
        guidance["previous_event_date"].notna()
    ].copy()

    # Adjusted EPS = currency-neutral EPS + currency impact.
    revisions["adjusted_revision_reconciliation"] = (
        revisions["change_adjusted_midpoint"]
        - revisions["change_currency_neutral_midpoint"]
        - revisions["change_currency_impact_forecast"]
    )

    # Reported EPS = adjusted EPS - forecast adjustments.
    revisions["reported_revision_reconciliation"] = (
        revisions["change_reported_midpoint"]
        - revisions["change_adjusted_midpoint"]
        + revisions["change_adjustments"]
    )

    tolerance = 0.011

    assert (
        revisions["adjusted_revision_reconciliation"]
        .abs()
        .max() < tolerance
    ), "Adjusted EPS guidance revision does not reconcile"

    assert (
        revisions["reported_revision_reconciliation"]
        .abs()
        .max() < tolerance
    ), "Reported EPS guidance revision does not reconcile"

    # Classify the drivers of each adjusted EPS revision.
    def classify_revision(row):
        currency_change = row[
            "change_currency_impact_forecast"
        ]

        neutral_change = row[
            "change_currency_neutral_midpoint"
        ]

        threshold = 0.001

        currency_changed = abs(currency_change) > threshold
        neutral_changed = abs(neutral_change) > threshold

        if currency_changed and neutral_changed:
            return "Currency and underlying guidance"
        elif currency_changed:
            return "Currency only"
        elif neutral_changed:
            return "Underlying guidance only"
        else:
            return "No adjusted EPS change"

    revisions["revision_driver"] = revisions.apply(
        classify_revision,
        axis=1,
    )

    output_columns = [
        "fiscal_year",
        "previous_event_date",
        "event_date",
        "event_type",
        "previous_adjusted_midpoint",
        "adjusted_midpoint",
        "change_adjusted_midpoint",
        "change_currency_neutral_midpoint",
        "change_currency_impact_forecast",
        "change_adjustments",
        "change_reported_midpoint",
        "revision_driver",
        "adjusted_revision_reconciliation",
        "reported_revision_reconciliation",
    ]

    revisions = revisions[output_columns]

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    revisions.to_csv(OUTPUT_FILE, index=False)

    print("\nPMI Guidance Revision Analysis")
    print("=" * 75)

    print(
        revisions[
            [
                "previous_event_date",
                "event_date",
                "change_adjusted_midpoint",
                "change_currency_neutral_midpoint",
                "change_currency_impact_forecast",
                "revision_driver",
            ]
        ].to_string(index=False)
    )

    print(f"\nExported: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
