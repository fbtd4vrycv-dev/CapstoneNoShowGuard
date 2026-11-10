"""Reproduce Task 2.2 clinic counts and no-show rates with pandas."""

from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
APPOINTMENTS_FILE = PROJECT_DIR / "appointments_clean.csv"
CLINICS_FILE = PROJECT_DIR / "clinics_enriched.csv"

EXPECTED_FILTERED = {
    "Hadapsar Care Centre": (143, 39, 27.3),
    "Malviya Nagar Clinic": (142, 38, 26.8),
    "Kothrud Family Clinic": (160, 36, 22.5),
    "Vijay Nagar Clinic": (101, 21, 20.8),
    "Edappally Medical Centre": (142, 23, 16.2),
    "Vaishali Nagar Clinic": (130, 18, 13.8),
}


def main():
    appointments = pd.read_csv(APPOINTMENTS_FILE)
    clinics = pd.read_csv(CLINICS_FILE)

    joined = appointments.merge(
        clinics[["clinic_id", "clinic_name", "city"]],
        on="clinic_id",
        how="inner",
        validate="many_to_one",
    )
    clinic_summary = (
        joined.groupby(["clinic_id", "clinic_name", "city"], as_index=False)
        .agg(appointments=("appointment_id", "size"), no_shows=("no_show", "sum"))
    )
    clinic_summary["no_show_pct"] = (
        100.0 * clinic_summary["no_shows"] / clinic_summary["appointments"]
    ).round(1)
    clinic_summary = clinic_summary.sort_values(
        "no_show_pct", ascending=False
    ).reset_index(drop=True)

    print("All clinics (equivalent to SQL query without HAVING):")
    print(clinic_summary[["clinic_name", "city", "appointments", "no_shows", "no_show_pct"]].to_string(index=False))

    filtered = clinic_summary[clinic_summary["appointments"] >= 95]
    print("\nClinics with at least 95 appointments:")
    print(filtered[["clinic_name", "city", "appointments", "no_shows", "no_show_pct"]].to_string(index=False))

    actual_filtered = {
        row.clinic_name: (row.appointments, row.no_shows, row.no_show_pct)
        for row in filtered.itertuples(index=False)
    }
    print("\nFiltered results match the acceptance criteria:", actual_filtered == EXPECTED_FILTERED)

    highest = clinic_summary.iloc[0]
    print(
        f"Highest-rate clinic overall: {highest['clinic_name']} ({highest['city']}), "
        f"{highest['no_show_pct']}% across {highest['appointments']} appointments"
    )
    print("Pandas row count after joining:", len(joined))
    print("Pandas clinic count:", clinic_summary["clinic_id"].nunique())


if __name__ == "__main__":
    main()
