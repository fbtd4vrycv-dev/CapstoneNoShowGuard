"""Create Task 1.4 features and NumPy summaries."""

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
CSV_FILE = PROJECT_DIR / "data" / "appointments.csv"


def main():
    # Prepare the data through Tasks 1.2 and 1.3 so this file runs by itself.
    df = pd.read_csv(CSV_FILE)
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
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        df[column] = np.clip(df[column], lower_fence, upper_fence)

    df["distance_km"] = df["distance_km"].round(1)
    df["fee_inr"] = df["fee_inr"].round().astype(int)

    # Create the requested features.
    df["lead_days"] = (df["appt_date"] - df["booked_on"]).dt.days
    df["no_show"] = (df["status"] == "No-Show").astype(int)

    # Build a NumPy array and compute the requested summaries without loops.
    X = df[["age", "distance_km", "fee_inr", "lead_days"]].to_numpy()
    print("Mean by column [age, distance_km, fee_inr, lead_days]:")
    print(np.mean(X, axis=0))

    mask = X[:, 3] > 14
    print("Rows with lead_days > 14:", mask.sum())
    print("Share of rows with lead_days > 14:", mask.mean())

    distance = X[:, 1]
    z_scores = (distance - np.mean(distance)) / np.std(distance)
    print("Rows with |distance_km z-score| > 2:", (np.abs(z_scores) > 2).sum())


if __name__ == "__main__":
    main()
