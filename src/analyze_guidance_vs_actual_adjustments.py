
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
ANALYSIS_DIR = BASE_DIR / "data" / "analysis"


def main():
    forecast = pd.read_csv(
        RAW_DIR / "guidance_adjustments_2025.csv",
        parse_dates=["event_date"],
    )
    actual = pd.read_csv(
        RAW_DIR / "actual_eps_adjustments_2025.csv"
    )
    guidance = pd.read_csv(
        ANALYSIS_DIR / "guidance_accuracy.csv",
        parse_dates=["event_date"],
    )

    forecast = forecast.rename(
        columns={"category": "adjustment_key",
                 "eps_impact": "forecast_impact"}
    )
    actual = actual.rename(
        columns={"eps_impact": "actual_impact"}
    )

    assert not forecast[
        ["fiscal_year", "event_date", "adjustment_key"]
    ].duplicated().any()

    assert not actual[
        ["fiscal_year", "adjustment_key"]
    ].duplicated().any()

    # Build a comparison for every event and every
    # adjustment appearing in either source.
    events = guidance[
        ["fiscal_year", "event_date"]
    ].drop_duplicates()

    actual_by_event = events.merge(
        actual,
        on="fiscal_year",
        how="left",
        validate="many_to_many",
    )

    comparison = forecast[
        ["fiscal_year", "event_date",
         "adjustment_key", "forecast_impact"]
    ].merge(
        actual_by_event[
            ["fiscal_year", "event_date",
             "adjustment_key", "actual_impact"]
        ],
        on=["fiscal_year", "event_date", "adjustment_key"],
        how="outer",
        validate="one_to_one",
    )

    comparison["forecast_included"] = (
        comparison["forecast_impact"].notna()
    )

    # Zero is used for analytical comparison only.
    # Missing forecast rows are not rewritten in raw data.
    comparison["forecast_impact"] = (
        comparison["forecast_impact"].fillna(0)
    )
    comparison["actual_impact"] = (
        comparison["actual_impact"].fillna(0)
    )

    comparison["adjustment_difference"] = (
        comparison["actual_impact"]
        - comparison["forecast_impact"]
    )

    comparison["status"] = comparison[
        "forecast_included"
    ].map({
        True: "Included in forecast",
        False: "Not included in forecast",
    })

    totals = comparison.groupby(
        ["fiscal_year", "event_date"],
        as_index=False
    )[["forecast_impact", "actual_impact",
       "adjustment_difference"]].sum()

    validation = totals.merge(
        guidance[
            ["fiscal_year", "event_date",
             "adjustments", "reported_forecast_error",
             "adjusted_forecast_error"]
        ],
        on=["fiscal_year", "event_date"],
        validate="one_to_one",
    )

    assert (
        validation["forecast_impact"]
        - validation["adjustments"]
    ).abs().max() < 0.001

    assert (
        validation["actual_impact"] - 0.28
    ).abs().max() < 0.001

    # Reported EPS error = adjusted EPS error
    #                      - adjustment difference.
    validation["bridge_residual"] = (
        validation["reported_forecast_error"]
        - validation["adjusted_forecast_error"]
        + validation["adjustment_difference"]
    )

    assert validation["bridge_residual"].abs().max() < 0.001

    comparison = comparison.sort_values(
        ["event_date", "adjustment_key"]
    )

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    comparison.to_csv(
        ANALYSIS_DIR / "guidance_actual_adjustments.csv",
        index=False,
    )
    validation.to_csv(
        ANALYSIS_DIR / "guidance_actual_adjustment_bridge.csv",
        index=False,
    )

    print("\nGuidance vs. Actual Adjustment Bridge")
    print("=" * 75)
    print(
        validation[
            ["event_date", "forecast_impact",
             "actual_impact", "adjustment_difference",
             "bridge_residual"]
        ].to_string(index=False)
    )

    print("\nBoth comparison exports created successfully.")


if __name__ == "__main__":
    main()
