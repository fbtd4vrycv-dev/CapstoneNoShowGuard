"""Clean appointment data for Task 1.3: validity, gaps, and outliers."""

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
CSV_FILE = PROJECT_DIR / "data" / "appointments.csv"


def main():
    # Start from the original CSV and repeat Task 1.2's preparation so this
    # file can be run on its own.
    df = pd.read_csv(CSV_FILE)
    df = df.drop_duplicates().copy()
    df["booking_channel"] = df["booking_channel"].str.strip().str.title()
    df["appt_date"] = pd.to_datetime(df["appt_date"], errors="coerce")
    df["booked_on"] = pd.to_datetime(df["booked_on"], errors="coerce")
    df = df.dropna(subset=["appt_date", "status"]).copy()

    # Ensure fields used in this task are numeric; unparseable entries become
    # missing and are handled by the median imputation below where applicable.
    for column in ("age", "distance_km", "fee_inr"):
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # (a) Ages outside the valid range are treated as missing.
    invalid_age = (df["age"] < 1) | (df["age"] > 100)
    df.loc[invalid_age, "age"] = np.nan

    # (b) Fill gaps before calculating quartiles and fences.
    age_median = df["age"].median()
    distance_median = df["distance_km"].median()
    df["age"] = df["age"].fillna(age_median).round().astype(int)
    df["distance_km"] = df["distance_km"].fillna(distance_median)

    # (c) Calculate fences on the filled data, then cap outliers at the fences.
    for column in ("distance_km", "fee_inr"):
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr

        capped_count = ((df[column] < lower_fence) | (df[column] > upper_fence)).sum()
        df[column] = np.clip(df[column], lower_fence, upper_fence)
        print(f"{column}: capped {capped_count} value(s)")

    # (d) Apply the requested final precision.
    df["distance_km"] = df["distance_km"].round(1)
    df["fee_inr"] = df["fee_inr"].round().astype(int)

    print("\nFinal shape:", df.shape)
    print("Missing values in age, distance_km, fee_inr:")
    print(df[["age", "distance_km", "fee_inr"]].isna().sum())


if __name__ == "__main__":
    main()
