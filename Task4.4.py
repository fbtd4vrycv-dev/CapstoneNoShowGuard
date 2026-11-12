"""Task 4.4: join note classifications to appointments and compare reminders."""

from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
NOTES_FILE = PROJECT_DIR / "notes_analysed.csv"
APPOINTMENTS_FILE = PROJECT_DIR / "appointments_clean.csv"


def main():
    notes = pd.read_csv(NOTES_FILE)
    appointments = pd.read_csv(APPOINTMENTS_FILE)
    merged = notes.merge(
        appointments[["appointment_id", "reminder_sent"]],
        on="appointment_id",
        how="left",
        validate="one_to_one",
    )

    if len(merged) != 10 or merged["reminder_sent"].isna().any():
        raise ValueError("Expected 10 notes, each matched to one appointment.")

    counts = pd.crosstab(merged["root_cause"], merged["reminder_sent"])
    forgot_notes = merged[merged["root_cause"] == "forgot_or_no_reminder"]
    forgot_without_reminder = int((forgot_notes["reminder_sent"] == "No").sum())
    no_reminder_count = int((merged["reminder_sent"] == "No").sum())

    print("Merged rows:", len(merged))
    print("\nRoot cause by reminder status:")
    print(counts.to_string())
    print(
        f"\nForgot/no-reminder notes with reminder_sent=No: "
        f"{forgot_without_reminder} of {len(forgot_notes)}"
    )
    print(f"Appointments with reminder_sent=No: {no_reminder_count} of {len(merged)}")


if __name__ == "__main__":
    main()
