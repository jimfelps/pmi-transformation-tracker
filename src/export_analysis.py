from pathlib import Path

from analysis import (
    get_transformation_summary,
    get_segment_growth_drivers,
    get_product_performance,
)


OUTPUT_DIR = Path("data/analysis")


def export_transformation_summary():
    """
    Export the quarter-level transformation
    scorecard used by the presentation layer.
    """

    summary = get_transformation_summary()

    output_file = (
        OUTPUT_DIR
        / "transformation_summary.csv"
    )

    summary.to_csv(
        output_file,
        index=False,
    )

    print(
        f"Transformation summary exported: "
        f"{output_file}"
    )

    return summary


def export_growth_drivers():
    """
    Export segment revenue and gross-profit
    growth drivers used for bridge analysis.
    """

    drivers = get_segment_growth_drivers()

    # The raw USD value is useful internally,
    # but the dashboard-ready dataset can use
    # the more readable millions-of-USD value.
    drivers = drivers[
        [
            "period_label",
            "segment_name",
            "metric_name",
            "driver_name",
            "value_millions",
            "driver_contribution_pct",
        ]
    ].copy()

    output_file = (
        OUTPUT_DIR
        / "growth_drivers.csv"
    )

    drivers.to_csv(
        output_file,
        index=False,
    )

    print(
        f"Growth drivers exported: "
        f"{output_file}"
    )

    return drivers

def export_product_performance():
    """
    Export smoke-free product shipment performance
    for the presentation layer.
    """

    products = get_product_performance()

    output_file = (
        OUTPUT_DIR
        / "product_performance.csv"
    )

    products.to_csv(
        output_file,
        index=False,
    )

    print(
        f"Product performance exported: "
        f"{output_file}"
    )

    return products


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = export_transformation_summary()
    drivers = export_growth_drivers()
    products = export_product_performance()

    print()
    print("Analysis export complete.")

    print(
        f"Transformation summary rows: "
        f"{len(summary)}"
    )

    print(
        f"Growth driver rows: "
        f"{len(drivers)}"
    )

    print(
        f"Product performance rows: "
        f"{len(products)}"
    )


if __name__ == "__main__":
    main()