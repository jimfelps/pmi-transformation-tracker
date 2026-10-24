
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
ANALYSIS_DIR = BASE_DIR / "data" / "analysis"


def main():
    adjustments = pd.read_csv(
        RAW_DIR / "guidance_adjustments_2025.csv",
        parse_dates=["event_date"],
    )

    guidance = pd.read_csv(
        ANALYSIS_DIR / "guidance_accuracy.csv",
        parse_dates=["event_date"],
    )

    # Prevent duplicate adjustment categories within an event.
    key = ["fiscal_year", "event_date", "category"]

    assert not adjustments[key].duplicated().any(), (
        "Duplicate guidance adjustment category"
    )

    # Reconcile individual adjustments to the published total.
    totals = (
        adjustments.groupby(
            ["fiscal_year", "event_date"],
            as_index=False,
        )["eps_impact"]
        .sum()
        .rename(columns={"eps_impact": "component_total"})
    )

    validation = guidance[
        ["fiscal_year", "event_date", "adjustments"]
    ].merge(
        totals,
        on=["fiscal_year", "event_date"],
        how="left",
        validate="one_to_one",
    )

    assert validation["component_total"].notna().all(), (
        "Missing adjustment components for a guidance event"
    )

    validation["difference"] = (
        validation["component_total"]
        - validation["adjustments"]
    ).round(4)

    assert (validation["difference"].abs() < 0.001).all(), (
        "Adjustment components do not reconcile to guidance"
    )

    # Create an event-by-category table for revision analysis.
    # Missing categories are zero-filled only in this analytical
    # comparison, not in the original source observations.
    matrix = adjustments.pivot_table(
        index=["fiscal_year", "event_date"],
        columns="category",
        values="eps_impact",
        aggfunc="sum",
        fill_value=0,
    ).sort_index()

    # Compare each event to the previous event within its year.
    changes = (
        matrix.groupby(level="fiscal_year")
        .diff()
        .dropna(how="all")
    )

    changes = changes.reset_index()

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    validation.to_csv(
        ANALYSIS_DIR / "guidance_adjustment_validation.csv",
        index=False,
    )

    changes.to_csv(
        ANALYSIS_DIR / "guidance_adjustment_changes.csv",
        index=False,
    )

    print("\nGuidance Adjustment Reconciliation")
    print("=" * 65)
    print(validation.to_string(index=False))

    print("\nAdjustment Changes by Guidance Event")
    print("=" * 65)
    print(changes.to_string(index=False))

    print("\nBoth adjustment exports created successfully.")


if __name__ == "__main__":
    main()
