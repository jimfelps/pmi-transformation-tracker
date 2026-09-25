from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = BASE_DIR / "data" / "analysis"

SUMMARY_FILE = ANALYSIS_DIR / "transformation_summary.csv"
DRIVERS_FILE = ANALYSIS_DIR / "growth_drivers.csv"
PRODUCT_FILE = ANALYSIS_DIR / "product_performance.csv"


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

    print("\nPMI Transformation Tracker — V1 QA")
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

    print("\n" + "=" * 60)
    print("V1 QA PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()