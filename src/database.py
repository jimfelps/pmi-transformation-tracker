from pathlib import Path
import sqlite3
import pandas as pd


DATABASE_DIR = Path("data")
DATABASE_FILE = DATABASE_DIR / "pmi_tracker.db"
SHIPMENTS_FILE = Path(
    "data/processed/quarterly_shipments.csv"
)
FINANCIALS_FILE = Path(
    "data/processed/quarterly_financials.csv"
)

def create_database():
    """
    Create the SQLite database and analytical schema.
    """

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_period (
            period_id INTEGER PRIMARY KEY,
            year INTEGER NOT NULL,
            quarter TEXT NOT NULL,
            period_label TEXT NOT NULL,
            period_order INTEGER NOT NULL,
            UNIQUE(year, quarter)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_metric (
            metric_id INTEGER PRIMARY KEY,
            metric_name TEXT NOT NULL UNIQUE,
            metric_group TEXT NOT NULL,
            unit TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_product (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_observation (
            observation_id INTEGER PRIMARY KEY,
            period_id INTEGER NOT NULL,
            metric_id INTEGER NOT NULL,
            product_id INTEGER,
            value REAL NOT NULL,
            source_type TEXT NOT NULL,
            source_document TEXT NOT NULL,
            derived INTEGER NOT NULL DEFAULT 0,
            
            UNIQUE(period_id, metric_id, product_id),

            FOREIGN KEY (period_id)
                REFERENCES dim_period(period_id),

            FOREIGN KEY (metric_id)
                REFERENCES dim_metric(metric_id),

            FOREIGN KEY (product_id)
                REFERENCES dim_product(product_id)
        )
    """)

    connection.commit()
    connection.close()

    print(
        f"Database created: {DATABASE_FILE}"
    )

PERIODS = [
    (2024, "Q1"),
    (2024, "Q2"),
    (2024, "Q3"),
    (2024, "Q4"),
    (2025, "Q1"),
    (2025, "Q2"),
    (2025, "Q3"),
    (2025, "Q4"),
    (2026, "Q1"),
    (2026, "Q2"),
]


METRICS = [
    ("revenue", "Financial", "USD"),
    ("operating_income", "Financial", "USD"),
    ("diluted_eps", "Financial", "USD/share"),
    ("operating_margin", "Financial", "ratio"),
    (
        "shipment_volume",
        "Volume",
        "billion_equivalent_units",
    ),
]


PRODUCTS = [
    "total",
    "smoke_free",
    "htu",
    "oral_sfp",
    "e_vapor",
    "cigarettes",
]

def main():
    create_database()
    load_dimensions()
    load_shipment_facts()
    load_financial_facts()

def load_dimensions():
    """
    Populate the analytical dimensions.
    """

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = connection.cursor()

    # Period dimension
    for year, quarter in PERIODS:

        quarter_number = int(
            quarter.replace("Q", "")
        )

        period_label = (
            f"{year}-{quarter}"
        )

        period_order = (
            year * 10 + quarter_number
        )

        cursor.execute(
            """
            INSERT OR IGNORE INTO dim_period (
                year,
                quarter,
                period_label,
                period_order
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                year,
                quarter,
                period_label,
                period_order,
            ),
        )

    # Metric dimension
    for (
        metric_name,
        metric_group,
        unit,
    ) in METRICS:

        cursor.execute(
            """
            INSERT OR IGNORE INTO dim_metric (
                metric_name,
                metric_group,
                unit
            )
            VALUES (?, ?, ?)
            """,
            (
                metric_name,
                metric_group,
                unit,
            ),
        )

    # Product dimension
    for product_name in PRODUCTS:

        cursor.execute(
            """
            INSERT OR IGNORE INTO dim_product (
                product_name
            )
            VALUES (?)
            """,
            (product_name,),
        )
        

    connection.commit()
    connection.close()

    print("Dimensions loaded.")

def get_dimension_id(
    cursor,
    table_name,
    id_column,
    lookup_column,
    lookup_value,
):
    """
    Return the surrogate key for a dimension member.
    """

    query = f"""
        SELECT {id_column}
        FROM {table_name}
        WHERE {lookup_column} = ?
    """

    cursor.execute(
        query,
        (lookup_value,),
    )

    result = cursor.fetchone()

    if result is None:
        raise ValueError(
            f"{lookup_value} not found "
            f"in {table_name}"
        )

    return result[0]

def load_shipment_facts():
    """
    Load quarterly shipment observations
    into the fact table.
    """

    shipments = pd.read_csv(
        SHIPMENTS_FILE
    )

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    cursor = connection.cursor()

    shipment_metric_id = get_dimension_id(
        cursor,
        "dim_metric",
        "metric_id",
        "metric_name",
        "shipment_volume",
    )

    product_columns = [
        "total",
        "smoke_free",
        "htu",
        "oral_sfp",
        "e_vapor",
        "cigarettes",
    ]

    for _, row in shipments.iterrows():

        cursor.execute(
            """
            SELECT period_id
            FROM dim_period
            WHERE year = ?
              AND quarter = ?
            """,
            (
                int(row["year"]),
                row["quarter"],
            ),
        )

        period_result = cursor.fetchone()

        if period_result is None:
            raise ValueError(
                f"Period not found: "
                f"{row['year']} "
                f"{row['quarter']}"
            )

        period_id = period_result[0]

        for product_name in product_columns:

            product_id = get_dimension_id(
                cursor,
                "dim_product",
                "product_id",
                "product_name",
                product_name,
            )

            cursor.execute(
                """
                INSERT OR REPLACE INTO fact_observation (
                    period_id,
                    metric_id,
                    product_id,
                    value,
                    source_type,
                    source_document,
                    derived
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    period_id,
                    shipment_metric_id,
                    product_id,
                    float(row[product_name]),
                    row["source_type"],
                    row["source_document"],
                    int(row["derived"]),
                ),
            )

    connection.commit()
    connection.close()

    print("Shipment facts loaded.")

def load_financial_facts():
    """
    Load quarterly financial observations
    into the fact table.
    """

    financials = pd.read_csv(
        FINANCIALS_FILE
    )

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    cursor = connection.cursor()

    financial_metrics = [
        "revenue",
        "operating_income",
        "diluted_eps",
        "operating_margin",
    ]

    for _, row in financials.iterrows():

        cursor.execute(
            """
            SELECT period_id
            FROM dim_period
            WHERE year = ?
              AND quarter = ?
            """,
            (
                int(row["year"]),
                row["quarter"],
            ),
        )

        period_result = cursor.fetchone()

        if period_result is None:
            raise ValueError(
                f"Period not found: "
                f"{row['year']} "
                f"{row['quarter']}"
            )

        period_id = period_result[0]

        for metric_name in financial_metrics:

            metric_id = get_dimension_id(
                cursor,
                "dim_metric",
                "metric_id",
                "metric_name",
                metric_name,
            )

            if metric_name == "operating_margin":
                derived = 1
            else:
                derived = int(row["derived"])

            cursor.execute(
                """
                DELETE FROM fact_observation
                WHERE period_id = ?
                    AND metric_id = ?
                    AND product_id IS NULL
                """,
                (
                    period_id,
                    metric_id,
                ),
            )

            cursor.execute(
                """
                INSERT OR REPLACE INTO fact_observation (
                    period_id,
                    metric_id,
                    product_id,
                    value,
                    source_type,
                    source_document,
                    derived
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    period_id,
                    metric_id,
                    None,
                    float(row[metric_name]),
                    row["source_type"],
                    row["source_document"],
                    derived,
                ),
            )

    connection.commit()
    connection.close()

    print("Financial facts loaded.")
    
if __name__ == "__main__":
    main()