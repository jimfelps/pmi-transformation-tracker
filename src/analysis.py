from pathlib import Path
import sqlite3
import pandas as pd


DATABASE_FILE = Path(
    "data/pmi_tracker.db"
)


def get_shipment_mix():
    """
    Calculate quarterly shipment mix
    by product category.
    """

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    query = """
        SELECT
            p.period_label,
            p.period_order,
            pr.product_name,
            f.value AS shipment_volume
        FROM fact_observation f
        JOIN dim_period p
            ON f.period_id = p.period_id
        JOIN dim_metric m
            ON f.metric_id = m.metric_id
        JOIN dim_product pr
            ON f.product_id = pr.product_id
        WHERE m.metric_name = 'shipment_volume'
        ORDER BY
            p.period_order,
            pr.product_name
    """

    shipments = pd.read_sql_query(
        query,
        connection,
    )

    connection.close()

    totals = (
        shipments[
            shipments["product_name"] == "total"
        ][
            [
                "period_label",
                "shipment_volume",
            ]
        ]
        .rename(
            columns={
                "shipment_volume":
                    "total_volume"
            }
        )
    )

    shipment_mix = shipments.merge(
        totals,
        on="period_label",
        how="left",
    )

    shipment_mix["shipment_mix"] = (
        shipment_mix["shipment_volume"]
        / shipment_mix["total_volume"]
    )

    return shipment_mix

def get_revenue_mix():
    """
    Calculate quarterly revenue mix
    by product category.
    """

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    query = """
        SELECT
            p.period_label,
            p.period_order,
            pr.product_name,
            f.value AS revenue
        FROM fact_observation f
        JOIN dim_period p
            ON f.period_id = p.period_id
        JOIN dim_metric m
            ON f.metric_id = m.metric_id
        JOIN dim_product pr
            ON f.product_id = pr.product_id
        WHERE m.metric_name = 'revenue'
        ORDER BY
            p.period_order,
            pr.product_name
    """

    revenue = pd.read_sql_query(
        query,
        connection,
    )

    connection.close()

    totals = (
        revenue[
            revenue["product_name"] == "total"
        ][
            [
                "period_label",
                "revenue",
            ]
        ]
        .rename(
            columns={
                "revenue":
                    "total_revenue"
            }
        )
    )

    revenue_mix = revenue.merge(
        totals,
        on="period_label",
        how="left",
    )

    revenue_mix["revenue_mix"] = (
        revenue_mix["revenue"]
        / revenue_mix["total_revenue"]
    )

    return revenue_mix

def get_smoke_free_mix_comparison():
    """
    Compare smoke-free shipment mix
    with smoke-free revenue mix.
    """

    shipments = get_shipment_mix()
    revenue = get_revenue_mix()

    smoke_free_shipments = shipments[
        shipments["product_name"]
        == "smoke_free"
    ][
        [
            "period_label",
            "shipment_mix",
        ]
    ]

    smoke_free_revenue = revenue[
        revenue["product_name"]
        == "smoke_free"
    ][
        [
            "period_label",
            "revenue_mix",
        ]
    ]

    comparison = (
        smoke_free_shipments
        .merge(
            smoke_free_revenue,
            on="period_label",
            how="inner",
        )
    )

    comparison[
        "revenue_mix_premium"
    ] = (
        comparison["revenue_mix"]
        - comparison["shipment_mix"]
    )

    return comparison

def get_shipment_yoy():
    """
    Calculate year-over-year shipment
    volume and mix changes.
    """

    shipment_mix = get_shipment_mix()

    shipment_mix["quarter"] = (
        shipment_mix["period_label"]
        .str.split("-")
        .str[1]
    )

    shipment_mix["year"] = (
        shipment_mix["period_label"]
        .str.split("-")
        .str[0]
        .astype(int)
    )

    shipment_mix = shipment_mix.sort_values(
        [
            "product_name",
            "quarter",
            "year",
        ]
    )

    shipment_mix["prior_year_volume"] = (
        shipment_mix
        .groupby(
            [
                "product_name",
                "quarter",
            ]
        )["shipment_volume"]
        .shift(1)
    )

    shipment_mix["prior_year_mix"] = (
        shipment_mix
        .groupby(
            [
                "product_name",
                "quarter",
            ]
        )["shipment_mix"]
        .shift(1)
    )

    shipment_mix["volume_yoy_pct"] = (
        shipment_mix["shipment_volume"]
        / shipment_mix["prior_year_volume"]
        - 1
    )

    shipment_mix["volume_change"] = (
        shipment_mix["shipment_volume"]
        - shipment_mix["prior_year_volume"]
    )

    shipment_mix["mix_yoy_change"] = (
        shipment_mix["shipment_mix"]
        - shipment_mix["prior_year_mix"]
    )

    smoke_free_growth = (
        shipment_mix[
            shipment_mix["product_name"]
            == "smoke_free"
        ][
            [
                "period_label",
                "volume_change",
            ]
        ]
        .rename(
            columns={
                "volume_change":
                    "smoke_free_volume_change"
            }
        )
    )

    shipment_mix = shipment_mix.merge(
        smoke_free_growth,
        on="period_label",
        how="left",
    )

    shipment_mix["sfp_growth_contribution"] = (
        shipment_mix["volume_change"]
        / shipment_mix[
            "smoke_free_volume_change"
        ]
    )

    return shipment_mix

def get_financial_yoy():
    """
    Calculate year-over-year changes
    in PMI financial performance.
    """

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    query = """
        SELECT
            p.year,
            p.quarter,
            p.period_label,
            p.period_order,
            m.metric_name,
            f.value
        FROM fact_observation f
        JOIN dim_period p
            ON f.period_id = p.period_id
        JOIN dim_metric m
            ON f.metric_id = m.metric_id
        WHERE m.metric_group = 'Financial'
        ORDER BY
            m.metric_name,
            p.period_order
    """

    financials = pd.read_sql_query(
        query,
        connection,
    )

    connection.close()

    financials["prior_year_value"] = (
        financials
        .groupby(
            [
                "metric_name",
                "quarter",
            ]
        )["value"]
        .shift(1)
    )

    financials["yoy_pct"] = (
        financials["value"]
        / financials["prior_year_value"]
        - 1
    )

    sign_change = (
        financials["value"]
        * financials["prior_year_value"]
        <= 0
    )

    financials.loc[
        sign_change,
        "yoy_pct",
    ] = pd.NA

    financials["yoy_change"] = (
        financials["value"]
        - financials["prior_year_value"]
    )

    financials["yoy_change_pp"] = (
        financials["yoy_change"] * 100
    )

    return financials

def get_transformation_scorecard():
    """
    Combine operational transformation
    and financial performance.
    """

    shipments = get_shipment_yoy()
    financials = get_financial_yoy()

    smoke_free = shipments[
        shipments["product_name"]
        == "smoke_free"
    ][
        [
            "period_label",
            "volume_yoy_pct",
            "mix_yoy_change",
        ]
    ].rename(
        columns={
            "volume_yoy_pct":
                "smoke_free_volume_yoy",
            "mix_yoy_change":
                "smoke_free_mix_change",
        }
    )

    cigarettes = shipments[
        shipments["product_name"]
        == "cigarettes"
    ][
        [
            "period_label",
            "volume_yoy_pct",
        ]
    ].rename(
        columns={
            "volume_yoy_pct":
                "cigarette_volume_yoy",
        }
    )

    financial_pivot = financials.pivot(
        index="period_label",
        columns="metric_name",
        values="yoy_pct",
    )

    financial_pivot = (
        financial_pivot
        .reset_index()
        .rename(
            columns={
                "revenue":
                    "revenue_yoy",
                "operating_income":
                    "operating_income_yoy",
                "diluted_eps":
                    "diluted_eps_yoy",
            }
        )
    )

    margin_change = financials[
        financials["metric_name"]
        == "operating_margin"
    ][
        [
            "period_label",
            "yoy_change_pp",
        ]
    ].rename(
        columns={
            "yoy_change_pp":
                "operating_margin_change_pp"
        }
    )

    financial_pivot = (
        financial_pivot
        .merge(
            margin_change,
            on="period_label",
            how="left",
        )
    )

    financial_pivot = financial_pivot[
        [
            "period_label",
            "revenue_yoy",
            "operating_income_yoy",
            "diluted_eps_yoy",
            "operating_margin_change_pp",
        ]
    ]

    scorecard = (
        smoke_free
        .merge(
            cigarettes,
            on="period_label",
            how="inner",
        )
        .merge(
            financial_pivot,
            on="period_label",
            how="inner",
        )
    )

    return scorecard

def main():

    comparison = (
        get_smoke_free_mix_comparison()
    )

    print(
        "PMI Smoke-Free Mix Comparison"
    )
    print("=" * 80)

    for _, row in comparison.iterrows():

        print()
        print(row["period_label"])

        print(
            f"  Shipment mix: "
            f"{row['shipment_mix']:.1%}"
        )

        print(
            f"  Revenue mix:  "
            f"{row['revenue_mix']:.1%}"
        )

        print(
            f"  Revenue mix premium: "
            f"{row['revenue_mix_premium'] * 100:+.1f} pp"
        )


if __name__ == "__main__":
    main()