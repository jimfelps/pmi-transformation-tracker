import json
from pathlib import Path


INPUT_FILE = Path("data/raw/pmi_companyfacts.json")


def inspect_concept(us_gaap, concept_name):
    """Print recent observations for a US-GAAP concept."""

    if concept_name not in us_gaap:
        print(f"\n{concept_name}: NOT FOUND")
        return

    concept = us_gaap[concept_name]

    print("\n" + "=" * 80)
    print(f"CONCEPT: {concept_name}")
    print(f"LABEL:   {concept.get('label')}")
    print(f"DESC:    {concept.get('description')}")
    print(f"UNITS:   {list(concept.get('units', {}).keys())}")

    # Most financial statement concepts will be reported in USD.
    units = concept.get("units", {})

    if "USD" not in units:
        print("No USD observations found.")
        return

    observations = units["USD"]

    # Show only recent 10-K and 10-Q observations.
    recent = [
        obs
        for obs in observations
        if obs.get("form") in ("10-K", "10-Q")
        and obs.get("end", "") >= "2024-01-01"
    ]

    print(f"\nRecent observations: {len(recent)}")
    print()

    for obs in recent:
        print(
            f"{obs.get('start')} → {obs.get('end')} | "
            f"FY={obs.get('fy')} | "
            f"FP={obs.get('fp')} | "
            f"FORM={obs.get('form')} | "
            f"VAL={obs.get('val'):,}"
        )


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    us_gaap = data["facts"]["us-gaap"]

    revenue_concepts = [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "RevenueFromRelatedParties",
        "SalesRevenueNet",
    ]

    for concept in revenue_concepts:
        inspect_concept(us_gaap, concept)


if __name__ == "__main__":
    main()