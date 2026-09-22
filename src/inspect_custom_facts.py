import json
from pathlib import Path


INPUT_FILE = Path("data/raw/pmi_companyfacts.json")


SEARCH_TERMS = [
    "shipment",
    "cigarette",
    "heated",
    "tobacco",
    "htu",
    "oral",
    "smoke",
    "vapor",
    "zyn",
]


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    print("Searching non-US-GAAP taxonomies...")
    print("=" * 80)

    for taxonomy_name, taxonomy in data["facts"].items():

        if taxonomy_name in ("us-gaap", "dei"):
            continue

        print(f"\nTAXONOMY: {taxonomy_name}")
        print(f"Concept count: {len(taxonomy)}")
        print("-" * 80)

        matches = []

        for concept_name, concept_data in taxonomy.items():

            label = concept_data.get("label") or ""
            description = concept_data.get("description") or ""

            search_text = (
                concept_name
                + " "
                + label
                + " "
                + description
            ).lower()

            if any(term in search_text for term in SEARCH_TERMS):
                matches.append(
                    (
                        concept_name,
                        label,
                        list(
                            concept_data.get(
                                "units",
                                {}
                            ).keys()
                        ),
                    )
                )

        if not matches:
            print("No matching concepts.")
            continue

        for concept_name, label, units in matches:
            print()
            print(f"Concept: {concept_name}")
            print(f"Label:   {label}")
            print(f"Units:   {units}")


if __name__ == "__main__":
    main()