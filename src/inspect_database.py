from pathlib import Path
import sqlite3


DATABASE_FILE = Path("data/pmi_tracker.db")


def main():
    connection = sqlite3.connect(
        DATABASE_FILE
    )

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


if __name__ == "__main__":
    main()