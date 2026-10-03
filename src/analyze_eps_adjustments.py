from pathlib import Path

import pandas as pd


INPUT_FILE = Path("data/raw/eps_adjustments.csv")


def main():
    df = pd.read_csv(INPUT_FILE)

    total_quarters = (
        df[["year", "quarter"]]
        .drop_duplicates()
        .shape[0]
    )

    category_summary = (
        df.groupby("category", as_index=False)
        .agg(
            occurrences=("eps_impact", "count"),
            cumulative_eps_impact=("eps_impact", "sum"),
            average_eps_impact=("eps_impact", "mean"),
            positive_quarters=("eps_impact", lambda x: (x > 0).sum()),
            negative_quarters=("eps_impact", lambda x: (x < 0).sum()),
            min_eps_impact=("eps_impact", "min"),
            max_eps_impact=("eps_impact", "max"),
        )
    )

    category_summary["quarter_frequency"] = (
        category_summary["occurrences"]
        / total_quarters
    )

    category_summary = category_summary.sort_values(
        "occurrences",
        ascending=False,
    )

    print()
    print("EPS Adjustment Frequency Analysis")
    print("=" * 85)
    print(f"Quarters analyzed: {total_quarters}")
    print()

    print(
        category_summary.to_string(
            index=False,
            formatters={
                "cumulative_eps_impact": lambda x: f"${x:+.2f}",
                "average_eps_impact": lambda x: f"${x:+.2f}",
                "quarter_frequency": lambda x: f"{x:.0%}",
                "min_eps_impact": lambda x: f"${x:+.2f}",
                "max_eps_impact": lambda x: f"${x:+.2f}",
            },
        )
    )


if __name__ == "__main__":
    main()