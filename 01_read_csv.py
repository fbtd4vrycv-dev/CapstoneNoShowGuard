"""Read and type-check the raw CareLoop appointments CSV (Task 1.1)."""

import csv
import json
from pathlib import Path


# The script looks for the original file inside this project's data folder.
PROJECT_DIR = Path(__file__).resolve().parent
CSV_FILE = PROJECT_DIR / "data" / "appointments.csv"
REJECTED_FILE = PROJECT_DIR / "rejected_rows.json"


def parse_row(row):
    """Return a copy of one CSV row with its numeric columns converted."""
    converted = dict(row)
    converted["age"] = int(row["age"])
    converted["fee_inr"] = int(row["fee_inr"])
    converted["prior_no_shows"] = int(row["prior_no_shows"])
    converted["distance_km"] = float(row["distance_km"])
    return converted


def main():
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {CSV_FILE}. Put the original appointments.csv "
            "inside a folder named data in this project."
        )

    # DictReader uses the first CSV row as column names.
    with CSV_FILE.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        print("Header:", reader.fieldnames)
        raw_rows = list(reader)

    print("Rows read:", len(raw_rows))

    accepted = []
    rejected = []

    # Blank or non-numeric values raise ValueError; keep those original rows
    # so they can be inspected instead of stopping the whole script.
    for row in raw_rows:
        try:
            accepted.append(parse_row(row))
        except ValueError:
            rejected.append(row)

    print("Accepted rows:", len(accepted))
    print("Rejected rows:", len(rejected))

    with REJECTED_FILE.open("w", encoding="utf-8") as file:
        json.dump(rejected, file, indent=2)

    print(f"Saved rejected rows to: {REJECTED_FILE.name}")


if __name__ == "__main__":
    main()
