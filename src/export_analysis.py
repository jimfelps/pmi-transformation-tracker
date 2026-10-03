from pathlib import Path

from analysis import (
    get_transformation_summary,
    get_segment_growth_drivers,
    get_product_performance,
    get_earnings_bridge,
    get_eps_reconciliation,
    get_eps_adjustment_history,
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

def export_earnings_bridge():
    """
    Export the PMI earnings bridge
    for the presentation layer.
    """

    bridge = get_earnings_bridge()

    output_file = (
        OUTPUT_DIR
        / "earnings_bridge.csv"
    )

    bridge.to_csv(
        output_file,
        index=False,
    )

    print(
        f"Earnings bridge exported: "
        f"{output_file}"
    )

    return bridge

def export_eps_reconciliation():
    """
    Export reported-to-adjusted EPS history
    for the presentation layer.
    """

    eps = get_eps_reconciliation()

    output_file = (
        OUTPUT_DIR
        / "eps_reconciliation.csv"
    )

    eps.to_csv(
        output_file,
        index=False,
    )

    print(
        f"EPS reconciliation exported: "
        f"{output_file}"
    )

    return eps

def export_eps_adjustment_history():
    """
    Export historical EPS adjustment detail
    and recurrence metrics.
    """

    history = get_eps_adjustment_history()

    output_file = (
        OUTPUT_DIR
        / "eps_adjustment_history.csv"
    )

    history.to_csv(
        output_file,
        index=False,
    )

    print(
        f"EPS adjustment history exported: "
        f"{output_file}"
    )

    return history

def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = export_transformation_summary()
    drivers = export_growth_drivers()
    products = export_product_performance()
    bridge = export_earnings_bridge()
    eps = export_eps_reconciliation()
    history = export_eps_adjustment_history()

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

    print(
        f"Earnings bridge rows: "
        f"{len(bridge)}"
    )

    print(
        f"EPS reconciliation rows: "
        f"{len(eps)}"
    )

    print(
        f"EPS adjustment history rows: "
        f"{len(history)}"
    )

if __name__ == "__main__":
    main()