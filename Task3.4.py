"""Task 3.4: evaluate a random forest and compare the three classifiers."""

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
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

    # Scale for logistic regression, fitting the scaler on training data only.
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    logistic = LogisticRegression(max_iter=1000)
    logistic.fit(X_train_s, y_train)

    depth_3_tree = DecisionTreeClassifier(max_depth=3, random_state=42)
    depth_3_tree.fit(X_train, y_train)

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    rf_train_accuracy = accuracy_score(y_train, rf.predict(X_train))
    rf_predictions = rf.predict(X_test)
    rf_probabilities = rf.predict_proba(X_test)[:, 1]

    print("Random forest:")
    print(f"Training accuracy: {rf_train_accuracy:.3f}")
    print(f"Test accuracy: {accuracy_score(y_test, rf_predictions):.3f}")
    print(f"Test recall: {recall_score(y_test, rf_predictions):.3f}")
    print(f"Test ROC-AUC: {roc_auc_score(y_test, rf_probabilities):.3f}")

    top_importances = sorted(
        zip(X.columns, rf.feature_importances_), key=lambda item: item[1], reverse=True
    )[:3]
    print("\nTop three random-forest feature importances:")
    for feature, importance in top_importances:
        print(f"{feature}: {importance:.3f}")

    model_results = []
    for name, model, test_features in [
        ("Logistic regression", logistic, X_test_s),
        ("Depth-3 tree", depth_3_tree, X_test),
        ("Random forest", rf, X_test),
    ]:
        predictions = model.predict(test_features)
        probabilities = model.predict_proba(test_features)[:, 1]
        model_results.append(
            {
                "Model": name,
                "Accuracy": accuracy_score(y_test, predictions),
                "Recall": recall_score(y_test, predictions),
                "ROC-AUC": roc_auc_score(y_test, probabilities),
            }
        )

    comparison = pd.DataFrame(model_results)
    print("\nTest-set comparison:")
    print(comparison.to_string(index=False, formatters={
        "Accuracy": "{:.3f}".format,
        "Recall": "{:.3f}".format,
        "ROC-AUC": "{:.3f}".format,
    }))

    best_by_auc = comparison.loc[comparison["ROC-AUC"].idxmax(), "Model"]
    print(
        f"\nBy test ROC-AUC, {best_by_auc} looks strongest at ranking no-show risk; "
        "the formal model choice in Task 3.5 should use training data only."
    )


if __name__ == "__main__":
    main()
