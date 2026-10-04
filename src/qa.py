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

    print("\n" + "=" * 60)
    print("PMI TRANSFORMATION TRACKER QA PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()