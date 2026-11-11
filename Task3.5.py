"""Task 3.5: select a model and threshold using training-only validation."""

from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import (
    GridSearchCV,
    cross_val_predict,
    cross_val_score,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "appointments_clean.csv"
RISK_SCORES_FILE = PROJECT_DIR / "test_risk_scores.csv"


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

    # Tune the forest using only training folds.
    forest_search = GridSearchCV(
        RandomForestClassifier(random_state=42),
        {"n_estimators": [100, 200], "max_depth": [3, 5, 8]},
        cv=5,
        scoring="roc_auc",
    )
    forest_search.fit(X_train, y_train)
    print("Tuned random forest:")
    print("Best parameters:", forest_search.best_params_)
    print(f"Best 5-fold CV ROC-AUC: {forest_search.best_score_:.3f}")

    lr_pipe = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000)),
        ]
    )
    depth_3_tree = DecisionTreeClassifier(max_depth=3, random_state=42)
    random_forest = RandomForestClassifier(n_estimators=100, random_state=42)

    candidates = [
        ("Logistic regression", lr_pipe),
        ("Depth-3 tree", depth_3_tree),
        ("Random forest", random_forest),
    ]
    cv_scores = {}
    print("\nTraining-set 5-fold CV ROC-AUC:")
    for name, model in candidates:
        score = cross_val_score(
            model, X_train, y_train, cv=5, scoring="roc_auc"
        ).mean()
        cv_scores[name] = score
        print(f"{name}: {score:.3f}")

    cv_scores["Tuned random forest"] = forest_search.best_score_
    print(f"Tuned random forest: {forest_search.best_score_:.3f}")

    models = {
        "Logistic regression": lr_pipe,
        "Depth-3 tree": depth_3_tree,
        "Random forest": random_forest,
        "Tuned random forest": forest_search.best_estimator_,
    }
    winner_name = max(cv_scores, key=cv_scores.get)
    winner = models[winner_name]
    print(
        f"\nChosen model: {winner_name} "
        f"(highest training-set CV ROC-AUC: {cv_scores[winner_name]:.3f})."
    )

    # OOF probabilities keep each training row out of its own fold's fit.
    oof_probabilities = cross_val_predict(
        winner, X_train, y_train, cv=5, method="predict_proba"
    )[:, 1]
    threshold_results = []
    print("\nOut-of-fold training threshold comparison:")
    for threshold in (0.5, 0.35):
        flags = (oof_probabilities >= threshold).astype(int)
        precision = precision_score(y_train, flags, zero_division=0)
        recall = recall_score(y_train, flags, zero_division=0)
        f1 = f1_score(y_train, flags, zero_division=0)
        threshold_results.append(
            {"threshold": threshold, "precision": precision, "recall": recall, "f1": f1}
        )
        print(
            f"Threshold {threshold:.2f}: precision={precision:.3f}, "
            f"recall={recall:.3f}, F1={f1:.3f}, flagged={int(flags.sum())}"
        )

    chosen_threshold = max(threshold_results, key=lambda result: result["f1"])[
        "threshold"
    ]
    print(
        f"Chosen threshold: {chosen_threshold:.2f} (higher out-of-fold F1)."
    )
    print(
        "Recall matters because a missed no-show warning can leave a slot empty, "
        "while an extra follow-up call costs about a minute."
    )

    # Fit the selected model on all training rows; evaluate the test set once.
    winner.fit(X_train, y_train)
    test_probabilities = winner.predict_proba(X_test)[:, 1]
    test_flags = (test_probabilities >= chosen_threshold).astype(int)
    print("\nOne-time test-set evaluation:")
    print(f"Threshold: {chosen_threshold:.2f}")
    print(
        f"Precision: {precision_score(y_test, test_flags, zero_division=0):.3f}"
    )
    print(f"Recall: {recall_score(y_test, test_flags, zero_division=0):.3f}")
    print(f"Number flagged: {int(test_flags.sum())}")
    print(f"ROC-AUC: {roc_auc_score(y_test, test_probabilities):.3f}")

    risk_scores = pd.DataFrame(
        {
            "appointment_id": df.loc[X_test.index, "appointment_id"].to_numpy(),
            "no_show": y_test.to_numpy(),
            "risk_prob": test_probabilities,
            "flag": test_flags,
        }
    )
    risk_scores.to_csv(RISK_SCORES_FILE, index=False)
    print(f"Saved {len(risk_scores)} test rows to {RISK_SCORES_FILE.name}.")

    print(
        "In practice, a clinic would set the threshold based on how many follow-up "
        "calls the front desk can make in an evening and the cost of an empty slot."
    )


if __name__ == "__main__":
    main()
