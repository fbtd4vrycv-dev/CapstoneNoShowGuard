"""Export the clean appointment CSV and SQL load statements for Task 1.6."""

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
APPOINTMENTS_FILE = PROJECT_DIR / "data" / "appointments.csv"
CLINICS_FILE = PROJECT_DIR / "clinics_enriched.csv"
APPOINTMENTS_OUTPUT = PROJECT_DIR / "appointments_clean.csv"
SQL_OUTPUT = PROJECT_DIR / "load_data.sql"

APPOINTMENT_COLUMNS = [
    "appointment_id", "patient_id", "clinic_id", "booked_on", "appt_date",
    "age", "gender", "distance_km", "fee_inr", "booking_channel",
    "visit_type", "reminder_sent", "prior_no_shows", "status", "lead_days",
    "no_show",
]
APPOINTMENT_NUMERIC_COLUMNS = {
    "age", "distance_km", "fee_inr", "prior_no_shows", "lead_days", "no_show"
}
CLINIC_NUMERIC_COLUMNS = {"latitude", "longitude", "temp_c"}


def sql_value(value, column, numeric_columns):
    """Format a CSV/DataFrame value as a SQL literal."""
    if pd.isna(value):
        return "NULL"
    if column in numeric_columns:
        if isinstance(value, (int, np.integer)):
            return str(int(value))
        if isinstance(value, (float, np.floating)):
            return str(int(value)) if float(value).is_integer() else format(float(value), ".15g")
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def main():
    if not CLINICS_FILE.exists():
        raise FileNotFoundError(
            f"Missing {CLINICS_FILE}. Run Task 1.5 first to create clinics_enriched.csv."
        )

    # Repeat Tasks 1.2–1.4 so this export script can run independently.
    df = pd.read_csv(APPOINTMENTS_FILE)
    df = df.drop_duplicates().copy()
    df["booking_channel"] = df["booking_channel"].str.strip().str.title()
    df["appt_date"] = pd.to_datetime(df["appt_date"], errors="coerce")
    df["booked_on"] = pd.to_datetime(df["booked_on"], errors="coerce")
    df = df.dropna(subset=["appt_date", "status"]).copy()

    for column in ("age", "distance_km", "fee_inr"):
        df[column] = pd.to_numeric(df[column], errors="coerce")
    invalid_age = (df["age"] < 1) | (df["age"] > 100)
    df.loc[invalid_age, "age"] = np.nan
    df["age"] = df["age"].fillna(df["age"].median()).round().astype(int)
    df["distance_km"] = df["distance_km"].fillna(df["distance_km"].median())

    for column in ("distance_km", "fee_inr"):
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        df[column] = np.clip(df[column], q1 - 1.5 * iqr, q3 + 1.5 * iqr)
    df["distance_km"] = df["distance_km"].round(1)
    df["fee_inr"] = df["fee_inr"].round().astype(int)

    df["lead_days"] = (df["appt_date"] - df["booked_on"]).dt.days
    df["no_show"] = (df["status"] == "No-Show").astype(int)
    df = df.sort_values("appointment_id").copy()
    df["booked_on"] = df["booked_on"].dt.strftime("%Y-%m-%d")
    df["appt_date"] = df["appt_date"].dt.strftime("%Y-%m-%d")
    df = df[APPOINTMENT_COLUMNS]

    id_is_unique = df["appointment_id"].is_unique
    columns_have_no_missing = not df.isna().any().any()
    print("appointment_id is unique:", id_is_unique)
    print("Missing values by export column:")
    print(df.isna().sum())
    print("No missing values in the 16 export columns:", columns_have_no_missing)
    if not id_is_unique or not columns_have_no_missing:
        raise ValueError("Appointment export validation failed; files were not written.")

    clinics = pd.read_csv(CLINICS_FILE)
    clinics_columns = list(clinics.columns)
    clinics_numeric_columns = CLINIC_NUMERIC_COLUMNS.intersection(clinics_columns)

    df.to_csv(APPOINTMENTS_OUTPUT, index=False)

    statements = []
    for _, clinic in clinics.iterrows():
        values = ",".join(
            sql_value(clinic[column], column, clinics_numeric_columns)
            for column in clinics_columns
        )
        statements.append(f"INSERT INTO clinics VALUES ({values});")

    for _, appointment in df.iterrows():
        values = ",".join(
            sql_value(appointment[column], column, APPOINTMENT_NUMERIC_COLUMNS)
            for column in APPOINTMENT_COLUMNS
        )
        statements.append(f"INSERT INTO appointments VALUES ({values});")

    SQL_OUTPUT.write_text("\n".join(statements) + "\n", encoding="utf-8")
    print(f"Saved {APPOINTMENTS_OUTPUT.name} and {SQL_OUTPUT.name}")


if __name__ == "__main__":
    main()
