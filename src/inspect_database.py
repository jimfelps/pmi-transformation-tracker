from pathlib import Path
import sqlite3
import pandas as pd


DATABASE_FILE = Path("data/pmi_tracker.db")

def inspect_bridge_facts():
    connection = sqlite3.connect(
        "data/pmi_tracker.db"
    )

    query = """
        SELECT
            p.period_label,
            s.segment_name,
            m.metric_name,
            d.driver_name,
            f.value / 1000000.0 AS value_millions,
            f.source_document
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

    print("\nSegment Bridge Facts")
    print("=" * 100)
    print(result.to_string(index=False))

def main():
    connection = sqlite3.connect(
        DATABASE_FILE
    )
    inspect_bridge_facts()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """)

    tables = cursor.fetchall()

    print("PMI Tracker Database")
    print("=" * 60)
    print()

    print("Tables:")

    for table in tables:
        print(f"  {table[0]}")

    print()
    print("Dimension Row Counts")
    print("=" * 60)

    dimension_tables = [
        "dim_period",
        "dim_metric",
        "dim_product",
    ]

    for table_name in dimension_tables:

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {table_name}
            """
        )

        count = cursor.fetchone()[0]

        print(
            f"{table_name}: {count}"
        )

    print()
    print("Fact Row Count")
    print("=" * 60)

    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_observation
    """)

    fact_count = cursor.fetchone()[0]

    print(
        f"fact_observation: {fact_count}"
    )

    print()
    print("Shipment Observations")
    print("=" * 60)

    cursor.execute("""
        SELECT
            p.period_label,
            m.metric_name,
            pr.product_name,
            f.value,
            f.source_document,
            f.derived
        FROM fact_observation f
        JOIN dim_period p
            ON f.period_id = p.period_id
        JOIN dim_metric m
            ON f.metric_id = m.metric_id
        LEFT JOIN dim_product pr
            ON f.product_id = pr.product_id
        WHERE m.metric_name = 'shipment_volume'
        ORDER BY
            p.period_order,
            pr.product_name
    """)

    observations = cursor.fetchall()

    for observation in observations:
        print(observation)

    print()
    print("Financial Observations")
    print("=" * 60)

    cursor.execute("""
        SELECT
            p.period_label,
            m.metric_name,
            f.value,
            m.unit,
            f.source_document,
            f.derived
        FROM fact_observation f
        JOIN dim_period p
            ON f.period_id = p.period_id
        JOIN dim_metric m
            ON f.metric_id = m.metric_id
        WHERE m.metric_group = 'Financial'
        ORDER BY
            p.period_order,
            m.metric_name
    """)

    financial_observations = cursor.fetchall()

    for observation in financial_observations:
        print(observation)

    connection.close()

print("\nRevenue Observation Structure:")

connection = sqlite3.connect("data/pmi_tracker.db")

query = """
SELECT
    p.period_label,
    m.metric_name,
    pr.product_name,
    s.segment_name,
    f.value,
    f.source_document,
    f.derived
FROM fact_observation f
JOIN dim_period p
    ON f.period_id = p.period_id
JOIN dim_metric m
    ON f.metric_id = m.metric_id
LEFT JOIN dim_product pr
    ON f.product_id = pr.product_id
LEFT JOIN dim_segment s
    ON f.segment_id = s.segment_id
WHERE m.metric_name = 'revenue'
  AND p.period_label = '2026-Q2'
ORDER BY
    CASE
        WHEN f.product_id IS NULL
         AND f.segment_id IS NULL THEN 1
        WHEN f.product_id IS NOT NULL THEN 2
        WHEN f.segment_id IS NOT NULL THEN 3
    END,
    pr.product_name,
    s.segment_name
"""

revenue_structure = pd.read_sql_query(
    query,
    connection,
)

connection.close()

print(revenue_structure.to_string(index=False))


if __name__ == "__main__":
    main()