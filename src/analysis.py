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
        WHERE m.metric_name IN (
            'revenue',
            'operating_income',
            'operating_margin',
            'diluted_eps'
        )
            AND f.product_id IS NULL
            AND f.segment_id IS NULL
            AND f.driver_id IS NULL
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

def get_product_revenue_yoy():

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    query = """
        SELECT
            p.period_label,
            p.year,
            p.quarter,
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

    revenue = revenue.sort_values(
        [
            "product_name",
            "year",
            "quarter",
        ]
    )

    revenue["prior_year_revenue"] = (
        revenue
        .groupby(
            [
                "product_name",
                "quarter",
            ]
        )["revenue"]
        .shift(1)
    )

    revenue["revenue_yoy_pct"] = (
        revenue["revenue"]
        / revenue["prior_year_revenue"]
        - 1
    )

    revenue["revenue_change"] = (
        revenue["revenue"]
        - revenue["prior_year_revenue"]
    )

    return revenue

def get_smoke_free_growth_comparison():

    shipment_yoy = get_shipment_yoy()
    revenue_yoy = get_product_revenue_yoy()

    shipment_sfp = (
        shipment_yoy[
            shipment_yoy["product_name"]
            == "smoke_free"
        ][
            [
                "period_label",
                "volume_yoy_pct",
            ]
        ]
        .copy()
    )

    revenue_sfp = (
        revenue_yoy[
            revenue_yoy["product_name"]
            == "smoke_free"
        ][
            [
                "period_label",
                "revenue_yoy_pct",
            ]
        ]
        .copy()
    )

    comparison = shipment_sfp.merge(
        revenue_sfp,
        on="period_label",
        how="inner",
    )

    comparison = comparison.dropna(
        subset=[
            "volume_yoy_pct",
            "revenue_yoy_pct",
        ]
    )

    comparison["revenue_volume_spread"] = (
        comparison["revenue_yoy_pct"]
        - comparison["volume_yoy_pct"]
    )

    return comparison

def get_product_growth_comparison(
    product_name,
    shipment_product_name=None,
):

    if shipment_product_name is None:
        shipment_product_name = product_name

    shipment_yoy = get_shipment_yoy()
    revenue_yoy = get_product_revenue_yoy()

    shipment_product = (
        shipment_yoy[
            shipment_yoy["product_name"]
            == shipment_product_name
        ][
            [
                "period_label",
                "volume_yoy_pct",
            ]
        ]
        .copy()
    )

    revenue_product = (
        revenue_yoy[
            revenue_yoy["product_name"]
            == product_name
        ][
            [
                "period_label",
                "revenue_yoy_pct",
            ]
        ]
        .copy()
    )

    comparison = shipment_product.merge(
        revenue_product,
        on="period_label",
        how="inner",
    )

    comparison = comparison.dropna(
        subset=[
            "volume_yoy_pct",
            "revenue_yoy_pct",
        ]
    )

    comparison["revenue_volume_spread"] = (
        comparison["revenue_yoy_pct"]
        - comparison["volume_yoy_pct"]
    )

    comparison["product_name"] = (
        product_name
    )

    return comparison

def get_segment_profitability_yoy():
    connection = sqlite3.connect(DATABASE_FILE)

    query = """
    SELECT
        p.period_label,
        p.year,
        p.quarter,
        s.segment_name,
        m.metric_name,
        f.value
    FROM fact_observation f
    JOIN dim_period p
        ON f.period_id = p.period_id
    JOIN dim_metric m
        ON f.metric_id = m.metric_id
    JOIN dim_segment s
        ON f.segment_id = s.segment_id
    WHERE m.metric_name IN (
        'revenue',
        'gross_profit',
        'gross_margin'
    )
    ORDER BY
        s.segment_name,
        p.year,
        p.quarter,
        m.metric_name
    """

    df = pd.read_sql_query(
        query,
        connection,
    )

    connection.close()

    # Convert the metric rows into one row per
    # period + segment.
    pivot = df.pivot_table(
        index=[
            "period_label",
            "year",
            "quarter",
            "segment_name",
        ],
        columns="metric_name",
        values="value",
    ).reset_index()

    # Sort before calculating prior-year values.
    pivot = pivot.sort_values(
        [
            "segment_name",
            "quarter",
            "year",
        ]
    )

    # Compare each quarter with the same quarter
    # in the previous year.
    pivot["prior_year_revenue"] = (
        pivot.groupby(
            ["segment_name", "quarter"]
        )["revenue"].shift(1)
    )

    pivot["prior_year_gross_profit"] = (
        pivot.groupby(
            ["segment_name", "quarter"]
        )["gross_profit"].shift(1)
    )

    pivot["prior_year_gross_margin"] = (
        pivot.groupby(
            ["segment_name", "quarter"]
        )["gross_margin"].shift(1)
    )

    pivot["revenue_yoy_pct"] = (
        pivot["revenue"]
        / pivot["prior_year_revenue"]
        - 1
    )

    pivot["gross_profit_yoy_pct"] = (
        pivot["gross_profit"]
        / pivot["prior_year_gross_profit"]
        - 1
    )

    pivot["gross_margin_change_pp"] = (
        pivot["gross_margin"]
        - pivot["prior_year_gross_margin"]
    ) * 100

    return pivot

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

def get_segment_growth_drivers():
    connection = sqlite3.connect(
        DATABASE_FILE
    )

    query = """
        SELECT
            p.period_label,
            s.segment_name,
            m.metric_name,
            d.driver_name,
            f.value
        FROM fact_observation f
        JOIN dim_period p
            ON f.period_id = p.period_id
        JOIN dim_metric m
            ON f.metric_id = m.metric_id
        JOIN dim_segment s
            ON f.segment_id = s.segment_id
        JOIN dim_driver d
            ON f.driver_id = d.driver_id
        WHERE m.metric_name IN (
            'revenue_change',
            'gross_profit_change'
        )
        ORDER BY
            p.period_order,
            s.segment_name,
            m.metric_name,
            d.driver_id
    """

    result = pd.read_sql_query(
        query,
        connection,
    )

    connection.close()

    # Display bridge values in millions.
    result["value_millions"] = (
        result["value"] / 1_000_000
    )

    # Calculate each driver's contribution relative
    # to the reported total change.
    totals = (
        result[
            result["driver_name"]
            == "total_change"
        ][
            [
                "period_label",
                "segment_name",
                "metric_name",
                "value",
            ]
        ]
        .rename(
            columns={
                "value": "total_change"
            }
        )
    )

    result = result.merge(
        totals,
        on=[
            "period_label",
            "segment_name",
            "metric_name",
        ],
        how="left",
    )

    result["driver_contribution_pct"] = (
        result["value"]
        / result["total_change"]
    )

    return result

def get_transformation_summary():
    """
    Build a quarter-level summary of PMI's transformation.

    This function composes existing analytical functions
    rather than querying the database directly.
    """

    # --------------------------------------------------
    # 1. Smoke-free mix
    # --------------------------------------------------

    mix = get_smoke_free_mix_comparison().copy()

    mix_summary = mix[
        [
            "period_label",
            "shipment_mix",
            "revenue_mix",
            "revenue_mix_premium",
        ]
    ].rename(
        columns={
            "shipment_mix": "smoke_free_shipment_mix",
            "revenue_mix": "smoke_free_revenue_mix",
            "revenue_mix_premium":
                "smoke_free_revenue_mix_premium",
        }
    )

    # --------------------------------------------------
    # 2. Smoke-free growth
    # --------------------------------------------------

    smoke_free_growth = (
        get_product_growth_comparison(
            "smoke_free"
        )
        .copy()
    )

    smoke_free_growth = smoke_free_growth[
        [
            "period_label",
            "volume_yoy_pct",
            "revenue_yoy_pct",
            "revenue_volume_spread",
        ]
    ].rename(
        columns={
            "volume_yoy_pct":
                "smoke_free_volume_growth",
            "revenue_yoy_pct":
                "smoke_free_revenue_growth",
            "revenue_volume_spread":
                "smoke_free_revenue_volume_spread",
        }
    )

    # --------------------------------------------------
    # 3. Combustible growth
    # --------------------------------------------------

    combustible_growth = (
        get_product_growth_comparison(
            "combustible",
            shipment_product_name="cigarettes",
        )
        .copy()
    )

    combustible_growth = combustible_growth[
        [
            "period_label",
            "volume_yoy_pct",
            "revenue_yoy_pct",
            "revenue_volume_spread",
        ]
    ].rename(
        columns={
            "volume_yoy_pct":
                "cigarette_volume_growth",
            "revenue_yoy_pct":
                "combustible_revenue_growth",
            "revenue_volume_spread":
                "combustible_revenue_volume_spread",
        }
    )

    # --------------------------------------------------
    # 4. Segment profitability
    # --------------------------------------------------

    segments = (
        get_segment_profitability_yoy()
        .copy()
    )

    segment_metrics = [
        "revenue_yoy_pct",
        "gross_profit_yoy_pct",
        "gross_margin",
        "gross_margin_change_pp",
    ]

    smoke_free_segment = segments[
        segments["segment_name"]
        == "international_smoke_free"
    ][
        ["period_label"] + segment_metrics
    ].rename(
        columns={
            "revenue_yoy_pct":
                "intl_sfp_revenue_growth",
            "gross_profit_yoy_pct":
                "intl_sfp_gross_profit_growth",
            "gross_margin":
                "intl_sfp_gross_margin",
            "gross_margin_change_pp":
                "intl_sfp_gross_margin_change_pp",
        }
    )

    combustible_segment = segments[
        segments["segment_name"]
        == "international_combustibles"
    ][
        ["period_label"] + segment_metrics
    ].rename(
        columns={
            "revenue_yoy_pct":
                "intl_comb_revenue_growth",
            "gross_profit_yoy_pct":
                "intl_comb_gross_profit_growth",
            "gross_margin":
                "intl_comb_gross_margin",
            "gross_margin_change_pp":
                "intl_comb_gross_margin_change_pp",
        }
    )

    # --------------------------------------------------
    # 5. Company financial performance
    # --------------------------------------------------

    company = (
        get_transformation_scorecard()
        .copy()
    )

    company_summary = company[
        [
            "period_label",
            "revenue_yoy",
            "operating_income_yoy",
            "diluted_eps_yoy",
            "operating_margin_change_pp",
        ]
    ].rename(
        columns={
            "revenue_yoy":
                "company_revenue_growth",
            "operating_income_yoy":
                "company_operating_income_growth",
            "diluted_eps_yoy":
                "company_eps_growth",
            "operating_margin_change_pp":
                "company_operating_margin_change_pp",
        }
    )

    # --------------------------------------------------
    # 6. Combine everything
    # --------------------------------------------------

    summary = mix_summary

    datasets = [
        smoke_free_growth,
        combustible_growth,
        smoke_free_segment,
        combustible_segment,
        company_summary,
    ]

    for dataset in datasets:
        summary = summary.merge(
            dataset,
            on="period_label",
            how="left",
        )

    return summary.sort_values(
        "period_label"
    ).reset_index(drop=True)

def main():
    summary = get_transformation_summary()

    print("\nPMI Transformation Summary")
    print("=" * 120)

    print(
        summary.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()