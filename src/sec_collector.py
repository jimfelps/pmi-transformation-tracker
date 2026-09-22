import json
from pathlib import Path

import requests


# Philip Morris International
CIK = "0001413329"

SEC_URL = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"

# SEC asks automated users to identify themselves.
# Replace the email below with your real email address.
HEADERS = {
    "User-Agent": "PMI Transformation Tracker jamesfelps@gmail.com"
}

RAW_DATA_DIR = Path("data/raw")
OUTPUT_FILE = RAW_DATA_DIR / "pmi_companyfacts.json"


def fetch_company_facts():
    """Download Philip Morris International XBRL company facts from the SEC."""

    print("Requesting PMI company facts from SEC EDGAR...")

    response = requests.get(
        SEC_URL,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def save_raw_data(data):
    """Save the untouched SEC response for later processing."""

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"Raw data saved to: {OUTPUT_FILE}")


def main():
    data = fetch_company_facts()

    print(f"Company: {data.get('entityName')}")
    print(f"CIK: {data.get('cik')}")

    save_raw_data(data)

    print("SEC collection complete.")


if __name__ == "__main__":
    main()