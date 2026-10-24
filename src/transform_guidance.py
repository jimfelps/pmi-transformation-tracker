
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
ANALYSIS_DIR = BASE_DIR / "data" / "analysis"


def main():
    guidance = pd.read_csv(
        RAW_DIR / "guidance_eps_2025.csv",
        parse_dates=["event_date"],
    )

    actuals = pd.read_csv(
        RAW_DIR / "guidance_actuals_2025.csv"
    )

    # Ensure we have exactly one actual result per fiscal year.
    assert actuals["fiscal_year"].is_unique

    # Each dated guidance observation must be unique.
    assert not guidance[
        ["fiscal_year", "event_date"]
    ].duplicated().any()

    # Calculate midpoints for each guidance measure.
    for metric in [
        "reported",
        "adjusted",
        "currency_neutral",
    ]:
        guidance[f"{metric}_midpoint"] = (
            guidance[f"{metric}_low"]
            + guidance[f"{metric}_high"]
        ) / 2

        assert (
            guidance[f"{metric}_low"]
            <= guidance[f"{metric}_high"]
        ).all()

    # Validate management's forecast reconciliations.
    tolerance = 0.011

    reported_to_adjusted = (
        guidance["adjusted_midpoint"]
        - guidance["reported_midpoint"]
    )

    assert (
        reported_to_adjusted
        - guidance["adjustments"]
    ).abs().max() < tolerance

    currency_reconciliation = (
        guidance["adjusted_midpoint"]
        - guidance["currency_neutral_midpoint"]
    )

    assert (
        currency_reconciliation
        - guidance["currency_impact"]
    ).abs().max() < tolerance

    # Join forecasts to the subsequently reported actuals.
    analysis = guidance.merge(
        actuals,
        on="fiscal_year",
        how="left",
        validate="many_to_one",
        suffixes=("_forecast", "_actual"),
    )

    assert analysis["adjusted_eps"].notna().all()

    # Positive error means actual performance exceeded guidance.
    for metric, actual_column in [
        ("reported", "reported_eps"),
        ("adjusted", "adjusted_eps"),
        ("currency_neutral", "currency_neutral_adjusted_eps"),
    ]:
        midpoint = analysis[f"{metric}_midpoint"]
        actual = analysis[actual_column]

        analysis[f"{metric}_forecast_error"] = actual - midpoint

        analysis[f"{metric}_within_range"] = (
            (actual >= analysis[f"{metric}_low"])
            & (actual <= analysis[f"{metric}_high"])
        )

    analysis = analysis.sort_values(
        ["fiscal_year", "event_date"]
    )

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    output = ANALYSIS_DIR / "guidance_accuracy.csv"

    analysis.to_csv(output, index=False)

    print("\nPMI FY2025 Guidance Accuracy")
    print("=" * 65)

    print(
        analysis[
            [
                "event_date",
                "adjusted_midpoint",
                "adjusted_eps",
                "adjusted_forecast_error",
                "adjusted_within_range",
            ]
        ].to_string(index=False)
    )

    print(f"\nExported: {output}")


if __name__ == "__main__":
    main()
