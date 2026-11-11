"""Task 3.2: fit scaled logistic regression and report test-set metrics."""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


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

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_s, y_train)

    y_pred = model.predict(X_test_s)
    y_prob = model.predict_proba(X_test_s)[:, 1]

    print("Test-set metrics:")
    print("Accuracy:", round(accuracy_score(y_test, y_pred), 3))
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))
    print("Precision:", round(precision_score(y_test, y_pred), 3))
    print("Recall:", round(recall_score(y_test, y_pred), 3))
    print("F1:", round(f1_score(y_test, y_pred), 3))
    print("ROC-AUC:", round(roc_auc_score(y_test, y_prob), 3))

    print("\nCoefficients (scaled features):")
    for feature, coefficient in zip(X.columns, model.coef_[0]):
        print(f"{feature}: {coefficient:+.3f}")

    reminder_index = X.columns.get_loc("reminder_sent")
    reminder_coefficient = model.coef_[0][reminder_index]
    reminder_scale = scaler.scale_[reminder_index]
    odds_ratio_per_sd = np.exp(reminder_coefficient)
    odds_ratio_no_to_yes = np.exp(reminder_coefficient / reminder_scale)

    print("\nReminder effect:")
    print(f"Odds ratio per 1 SD: {odds_ratio_per_sd:.3f}")
    print(f"Odds ratio for No -> Yes: {odds_ratio_no_to_yes:.3f}")
    print(
        "These differ because the first odds ratio is for a one-standard-deviation "
        f"change (SD = {reminder_scale:.3f}), while No -> Yes is a full one-unit change."
    )
    print(
        "Association: in this model, holding the other features constant, a reminder "
        f"is associated with {100 * (1 - odds_ratio_no_to_yes):.1f}% lower odds of a "
        "no-show; because the data are observational, this does not show that reminders cause fewer no-shows."
    )


if __name__ == "__main__":
    main()
