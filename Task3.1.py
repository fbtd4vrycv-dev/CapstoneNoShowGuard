"""Task 3.1: prepare features, make the fixed split, and report the baseline."""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "appointments_clean.csv"


def main():
    # Keep the CSV's existing row order; the fixed split depends on it.
    df = pd.read_csv(DATA_FILE)

    feature_columns = [
        "age",
        "distance_km",
        "fee_inr",
        "lead_days",
        "prior_no_shows",
        "reminder_sent",
        "booking_channel",
        "visit_type",
    ]
    X = df[feature_columns].copy()
    X["reminder_sent"] = X["reminder_sent"].map({"Yes": 1, "No": 0})
    X = pd.get_dummies(X, columns=["booking_channel", "visit_type"])
    y = df["no_show"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    test_no_shows = int(y_test.sum())
    baseline_accuracy = (y_test == 0).mean()  # Always predict Attended (no_show=0).

    print("Feature columns ({}):".format(X.shape[1]), list(X.columns))
    print("Training rows:", len(X_train))
    print("Test rows:", len(X_test))
    print("No-shows in test set:", test_no_shows)
    print("Overall no-show rate:", round(y.mean() * 100, 1), "%")
    print("Baseline accuracy (always predict Attended):", round(baseline_accuracy, 4))


if __name__ == "__main__":
    main()
