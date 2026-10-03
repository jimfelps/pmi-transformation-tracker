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

    units = concept.get("units", {})

    if not units:
        print("No observations found.")
        return

    unit_name = list(units.keys())[0]
    observations = units[unit_name]

    print(f"Using unit: {unit_name}")

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

def search_concepts(us_gaap, search_terms):
    """Search US-GAAP concepts by concept name and label."""

    print("\n" + "=" * 80)
    print("CONCEPT SEARCH")

    for search_term in search_terms:
        print(f"\nSearch term: {search_term}")
        print("-" * 40)

        matches = []

        for concept_name, concept in us_gaap.items():
            label = concept.get("label", "")

            searchable_text = f"{concept_name} {label}".lower()

            if search_term.lower() in searchable_text:
                matches.append((concept_name, label))

        if not matches:
            print("No matches found.")
            continue

        for concept_name, label in matches:
            print(f"{concept_name}")
            print(f"    {label}")

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    us_gaap = data["facts"]["us-gaap"]

    concepts_to_inspect = [
        "OperatingIncomeLoss",
        "InterestIncomeExpenseNonoperatingNet",
        "NetPeriodicDefinedBenefitsExpenseReversalOfExpenseExcludingServiceCostComponent",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
        "IncomeTaxExpenseBenefit",
        "IncomeLossFromEquityMethodInvestments",
        "ProfitLoss",
        "NetIncomeLossAttributableToNoncontrollingInterest",
        "NetIncomeLoss",
        "EquitySecuritiesWithoutReadilyDeterminableFairValueImpairmentLossAnnualAmount"
    ]

    for concept in concepts_to_inspect:
        inspect_concept(us_gaap, concept)

    search_terms = [
        "interest",
        "income before",
        "income tax",
        "pension",
        "benefit",
        "equity",
        "impairment",
    ]

    # search_concepts(us_gaap, search_terms)

if __name__ == "__main__":
    main()