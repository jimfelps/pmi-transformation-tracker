from pathlib import Path

import requests


HEADERS = {
    "User-Agent": "PMI Transformation Tracker jamesfelps@gmail.com"
}

RAW_DIR = Path("data/raw/filings")


FILINGS = {
    "2024-Q1": "https://www.sec.gov/Archives/edgar/data/1413329/000141332924000087/pm-20240331.htm",
    "2024-Q2": "https://www.sec.gov/Archives/edgar/data/1413329/000141332924000145/pm-20240630.htm",
    "2024-Q3": "https://www.sec.gov/Archives/edgar/data/1413329/000141332924000172/pm-20240930.htm",

    "2025-Q1": "https://www.sec.gov/Archives/edgar/data/1413329/000141332925000094/pm-20250331.htm",
    "2025-Q2": "https://www.sec.gov/Archives/edgar/data/1413329/000141332925000150/pm-20250630.htm",
    "2025-Q3": "https://www.sec.gov/Archives/edgar/data/1413329/000162828025046179/pm-20250930.htm",

    "2026-Q1": "https://www.sec.gov/Archives/edgar/data/1413329/000162828026027019/pm-20260331.htm",
    "2026-Q2": "https://www.sec.gov/Archives/edgar/data/1413329/000162828026049493/pm-20260630.htm",
    "2024-FY": "https://www.sec.gov/Archives/edgar/data/1413329/000141332925000013/pm-20241231.htm",
    "2025-FY": "https://www.sec.gov/Archives/edgar/data/1413329/000162828026005939/pm-20251231.htm",
}


def download_filing(period, url):
    """Download one SEC filing and save the raw HTML."""

    output_file = RAW_DIR / f"{period}.html"

    print(f"Downloading {period}...")

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    output_file.write_text(
        response.text,
        encoding="utf-8",
    )

    print(
        f"  Saved {len(response.text):,} characters "
        f"to {output_file}"
    )


def main():
    RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for period, url in FILINGS.items():
        download_filing(period, url)

    print()
    print("PMI filing collection complete.")


if __name__ == "__main__":
    main()