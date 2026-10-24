from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = BASE_DIR / "data" / "analysis"

SUMMARY_FILE = ANALYSIS_DIR / "transformation_summary.csv"
DRIVERS_FILE = ANALYSIS_DIR / "growth_drivers.csv"
PRODUCT_FILE = ANALYSIS_DIR / "product_performance.csv"
EARNINGS_BRIDGE_FILE = ANALYSIS_DIR / "earnings_bridge.csv"
EPS_RECONCILIATION_FILE = ANALYSIS_DIR / "eps_reconciliation.csv"
EPS_ADJUSTMENT_HISTORY_FILE = ANALYSIS_DIR / "eps_adjustment_history.csv"

GUIDANCE_ACCURACY_FILE = ANALYSIS_DIR / "guidance_accuracy.csv"
GUIDANCE_REVISIONS_FILE = ANALYSIS_DIR / "guidance_revisions.csv"

GUIDANCE_ADJUSTMENT_VALIDATION_FILE = (
    ANALYSIS_DIR / "guidance_adjustment_validation.csv"
)

GUIDANCE_ADJUSTMENT_CHANGES_FILE = (
    ANALYSIS_DIR / "guidance_adjustment_changes.csv"
)

GUIDANCE_ACTUAL_ADJUSTMENTS_FILE = (
    ANALYSIS_DIR / "guidance_actual_adjustments.csv"
)

GUIDANCE_ACTUAL_BRIDGE_FILE = (
    ANALYSIS_DIR / "guidance_actual_adjustment_bridge.csv"
)

def check(condition, message):
    if condition:
        print(f"PASS  {message}")
    else:
        print(f"FAIL  {message}")
        raise AssertionError(message)


def main():
    summary = pd.read_csv(SUMMARY_FILE)
    drivers = pd.read_csv(DRIVERS_FILE)
    products = pd.read_csv(PRODUCT_FILE)
    earnings_bridge = pd.read_csv(EARNINGS_BRIDGE_FILE)
    eps_reconciliation = pd.read_csv(EPS_RECONCILIATION_FILE)
    eps_adjustments = pd.read_csv(EPS_ADJUSTMENT_HISTORY_FILE)

    print("\nPMI Transformation Tracker — QA")
    print("=" * 60)

    # --------------------------------------------------
    # File / row checks
    # --------------------------------------------------

    check(
        len(summary) == 6,
        "Transformation summary contains 6 quarters",
    )

    check(
        len(drivers) == 44,
        "Growth-driver dataset contains 44 observations",
    )

    check(
        len(products) == 18,
        "Product-performance dataset contains 18 observations",
    )

    check(
        len(earnings_bridge) == 7,
        "Earnings bridge contains 7 components",
    )

    check(
        len(eps_reconciliation) == 10,
        "EPS reconciliation contains 10 quarters",
    )

    check(
        len(eps_adjustments) == 49,
        "EPS adjustment history contains 49 observations",
    )

    # --------------------------------------------------
    # Key uniqueness
    # --------------------------------------------------

    check(
        not summary["period_label"].duplicated().any(),
        "Transformation summary has one row per period",
    )

    check(
        not products[
            ["period_label", "product_name"]
        ].duplicated().any(),
        "Product performance has unique period/product rows",
    )

    check(
        not drivers[
            [
                "period_label",
                "metric_name",
                "segment_name",
                "driver_name",
            ]
        ].duplicated().any(),
        "Growth drivers have unique analytical keys",
    )

    check(
        not earnings_bridge["component"].duplicated().any(),
        "Earnings bridge has one row per component",
    )

    check(
        not eps_reconciliation["period_label"].duplicated().any(),
        "EPS reconciliation has one row per period",
    )

    check(
        not eps_adjustments[
            ["period_label", "adjustment"]
        ].duplicated().any(),
        "EPS adjustment history has unique period/adjustment rows",
    )

    # --------------------------------------------------
    # Latest-period checks
    # --------------------------------------------------

    latest_period = summary["period_label"].max()

    check(
        latest_period == "2026-Q2",
        "Latest summary period is 2026-Q2",
    )

    latest = summary[
        summary["period_label"] == latest_period
    ].iloc[0]

    check(
        0 <= latest["smoke_free_shipment_mix"] <= 1,
        "Smoke-free shipment mix is a valid percentage",
    )

    check(
        0 <= latest["smoke_free_revenue_mix"] <= 1,
        "Smoke-free revenue mix is a valid percentage",
    )

    check(
        latest["smoke_free_revenue_mix"]
        > latest["smoke_free_shipment_mix"],
        "Smoke-free revenue mix exceeds shipment mix",
    )

    # --------------------------------------------------
    # Product reconciliation
    # --------------------------------------------------

    latest_products = products[
        products["period_label"] == latest_period
    ]

    check(
        set(latest_products["product_name"])
        == {"htu", "oral_sfp", "e_vapor"},
        "Latest period contains all three smoke-free product categories",
    )

    # --------------------------------------------------
    # Bridge reconciliation
    # --------------------------------------------------

    bridge_groups = drivers.groupby(
        [
            "period_label",
            "metric_name",
            "segment_name",
        ]
    )

    for key, group in bridge_groups:

        total = group.loc[
            group["driver_name"] == "total_change",
            "value_millions",
        ]

        components = group.loc[
            group["driver_name"] != "total_change",
            "value_millions",
        ].sum()

        check(
            len(total) == 1,
            f"{key} has one total-change observation",
        )

        difference = abs(
            total.iloc[0] - components
        )

        check(
            difference <= 2,
            f"{key} bridge reconciles within $2M",
        )

    # --------------------------------------------------
    # Earnings bridge reconciliation
    # --------------------------------------------------

    bridge_total = earnings_bridge["value_millions"].sum()

    check(
        abs(bridge_total - (-222)) < 0.01,
        "Earnings bridge reconciles to $222M decline in PMI earnings",
    )

    # --------------------------------------------------
    # EPS reconciliation
    # --------------------------------------------------

    reported_adjusted = eps_reconciliation.dropna(
        subset=["reported_adjusted_eps"]
    )

    check(
        len(reported_adjusted) == 8,
        "Eight quarters have independently reported adjusted EPS",
    )

    max_eps_difference = (
        reported_adjusted["adjusted_eps"]
        - reported_adjusted["reported_adjusted_eps"]
    ).abs().max()

    check(
        max_eps_difference < 0.001,
        "Calculated adjusted EPS reconciles to PMI-reported adjusted EPS",
    )

    # --------------------------------------------------
    # Non-additive Q4 protection
    # --------------------------------------------------

    q4_eps = eps_reconciliation[
        eps_reconciliation["quarter"] == "Q4"
    ]

    check(
        q4_eps["diluted_eps"].isna().all(),
        "Q4 diluted EPS is not derived by subtraction",
    )

    check(
        q4_eps["adjusted_eps"].isna().all(),
        "Q4 adjusted EPS is not derived by subtraction",
    )

        
    # ==========================================================
    # V2.2 — Guidance vs. Actuals
    # ==========================================================

    print("\nV2.2 — Guidance vs. Actuals")
    print("-" * 60)

    guidance = pd.read_csv(GUIDANCE_ACCURACY_FILE)
    revisions = pd.read_csv(GUIDANCE_REVISIONS_FILE)

    adjustment_validation = pd.read_csv(
        GUIDANCE_ADJUSTMENT_VALIDATION_FILE
    )

    adjustment_changes = pd.read_csv(
        GUIDANCE_ADJUSTMENT_CHANGES_FILE
    )

    actual_adjustments = pd.read_csv(
        GUIDANCE_ACTUAL_ADJUSTMENTS_FILE
    )

    actual_bridge = pd.read_csv(
        GUIDANCE_ACTUAL_BRIDGE_FILE
    )

    tolerance = 0.001

    # ----------------------------------------------------------
    # Dataset structure
    # ----------------------------------------------------------

    check(
        len(guidance) == 4,
        "FY2025 guidance contains four forecast observations",
    )

    check(
        len(revisions) == 3,
        "FY2025 guidance contains three revisions",
    )

    check(
        len(adjustment_validation) == 4,
        "Four guidance adjustment totals are validated",
    )

    check(
        len(adjustment_changes) == 3,
        "Three adjustment revision observations exist",
    )

    check(
        len(actual_adjustments) == 40,
        "Forecast vs. actual adjustment comparison contains 40 rows",
    )

    check(
        len(actual_bridge) == 4,
        "Four forecast-to-actual adjustment bridges exist",
    )

    # ----------------------------------------------------------
    # Uniqueness
    # ----------------------------------------------------------

    check(
        not guidance[
            ["fiscal_year", "event_date"]
        ].duplicated().any(),
        "Guidance observations have unique year/date keys",
    )

    check(
        not revisions[
            ["fiscal_year", "event_date"]
        ].duplicated().any(),
        "Guidance revisions have unique year/date keys",
    )

    check(
        not actual_adjustments[
            ["fiscal_year", "event_date", "adjustment_key"]
        ].duplicated().any(),
        "Forecast vs. actual adjustments have unique keys",
    )

    check(
        not actual_bridge[
            ["fiscal_year", "event_date"]
        ].duplicated().any(),
        "Adjustment bridges have unique year/date keys",
    )

    # ----------------------------------------------------------
    # Guidance forecast accuracy
    # ----------------------------------------------------------

    check(
        (guidance["fiscal_year"] == 2025).all(),
        "V2.2 guidance is scoped to FY2025",
    )

    check(
        (
            guidance["adjusted_eps"]
            - guidance["adjusted_midpoint"]
            - guidance["adjusted_forecast_error"]
        ).abs().max() < tolerance,
        "Adjusted EPS forecast errors reconcile",
    )

    check(
        (
            guidance["reported_eps"]
            - guidance["reported_midpoint"]
            - guidance["reported_forecast_error"]
        ).abs().max() < tolerance,
        "Reported EPS forecast errors reconcile",
    )

    check(
        (
            guidance["adjusted_midpoint"]
            - guidance["reported_midpoint"]
            - guidance["adjustments"]
        ).abs().max() < tolerance,
        "Forecast reported-to-adjusted EPS reconciles",
    )

    check(
        (
            guidance["adjusted_midpoint"]
            - guidance["currency_neutral_midpoint"]
            - guidance["currency_impact_forecast"]
        ).abs().max() < tolerance,
        "Forecast currency impact reconciles",
    )

    # ----------------------------------------------------------
    # Guidance revision decomposition
    # ----------------------------------------------------------

    check(
        (
            revisions["change_adjusted_midpoint"]
            - revisions["change_currency_neutral_midpoint"]
            - revisions["change_currency_impact_forecast"]
        ).abs().max() < tolerance,
        "Adjusted EPS revisions reconcile to underlying and currency",
    )

    check(
        (
            revisions["change_reported_midpoint"]
            - revisions["change_adjusted_midpoint"]
            + revisions["change_adjustments"]
        ).abs().max() < tolerance,
        "Reported EPS revisions reconcile to adjustment changes",
    )

    check(
        revisions[
            "adjusted_revision_reconciliation"
        ].abs().max() < tolerance,
        "Stored adjusted EPS revision residuals are zero",
    )

    check(
        revisions[
            "reported_revision_reconciliation"
        ].abs().max() < tolerance,
        "Stored reported EPS revision residuals are zero",
    )

    # ----------------------------------------------------------
    # Forecast adjustment components
    # ----------------------------------------------------------

    check(
        adjustment_validation["component_total"].notna().all(),
        "All guidance events contain adjustment components",
    )

    check(
        (
            adjustment_validation["component_total"]
            - adjustment_validation["adjustments"]
        ).abs().max() < tolerance,
        "Forecast adjustment components reconcile to published totals",
    )

    check(
        (
            adjustment_changes
            .select_dtypes(include="number")
            .drop(columns=["fiscal_year"], errors="ignore")
            .sum(axis=1)
            .notna()
        ).all(),
        "Adjustment revision values are numeric",
    )

    # ----------------------------------------------------------
    # Forecast vs. annual actual adjustments
    # ----------------------------------------------------------

    check(
        (
            actual_bridge["forecast_impact"]
            - actual_bridge["adjustments"]
        ).abs().max() < tolerance,
        "Forecast adjustment bridge ties to guidance",
    )

    check(
        (
            actual_bridge["actual_impact"] - 0.28
        ).abs().max() < tolerance,
        "FY2025 annual actual adjustments equal $0.28",
    )

    check(
        (
            actual_bridge["actual_impact"]
            - actual_bridge["forecast_impact"]
            - actual_bridge["adjustment_difference"]
        ).abs().max() < tolerance,
        "Actual minus forecast adjustment difference reconciles",
    )

    check(
        (
            actual_bridge["reported_forecast_error"]
            - actual_bridge["adjusted_forecast_error"]
            + actual_bridge["adjustment_difference"]
        ).abs().max() < tolerance,
        "Reported EPS forecast error bridge reconciles",
    )

    check(
        actual_bridge["bridge_residual"].abs().max() < tolerance,
        "All stored forecast-to-actual bridge residuals are zero",
    )


    print("\n" + "=" * 60)
    print("PMI TRANSFORMATION TRACKER QA PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()