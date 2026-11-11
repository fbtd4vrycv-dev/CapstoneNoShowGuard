"""Task 3.3: compare decision-tree depth and check for overfitting."""

from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "appointments_clean.csv"


def main():
    # Match Task 3.1's feature order, encoding, and fixed split exactly.
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

    trees = [
        ("Full-depth tree", DecisionTreeClassifier(random_state=42)),
        ("Depth-3 tree", DecisionTreeClassifier(max_depth=3, random_state=42)),
    ]

    for name, model in trees:
        model.fit(X_train, y_train)
        train_accuracy = accuracy_score(y_train, model.predict(X_train))
        test_accuracy = accuracy_score(y_test, model.predict(X_test))
        print(f"{name} (actual depth: {model.get_depth()}):")
        print(f"  Training accuracy: {train_accuracy:.3f}")
        print(f"  Test accuracy:     {test_accuracy:.3f}")

    print(
        "The full-depth tree's much higher training than test accuracy shows "
        "overfitting: it memorizes training patterns that do not generalize well."
    )


if __name__ == "__main__":
    main()
