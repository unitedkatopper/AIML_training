import os
import pandas as pd
import joblib
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score
)

DATA_FILE = "data/attempts.csv"
MODEL_DIR = "models"
RESULT_DIR = "results"

features = [
    "creativity", "originality", "problem_solving", "research_aptitude",
    "invention_thinking", "pattern_recognition", "risk_taking"
]


def make_level(score):
    if score >= 80:
        return "High"
    elif score >= 60:
        return "Medium"
    return "Low"


def safe_round(x):
    try:
        return round(float(x), 3)
    except Exception:
        return x


def main():
    if not os.path.exists(DATA_FILE):
        print("No data found. First run the app and collect some attempts.")
        return

    df = pd.read_csv(DATA_FILE)
    if len(df) < 5:
        print("You have data, but very less attempts.")
        print("At least 5 attempts are needed for demo training. 30+ will be better.")
        return

    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(RESULT_DIR, exist_ok=True)

    # keep only needed columns and remove incomplete rows
    df = df.dropna(subset=features + ["innovation_score"])

    X = df[features]
    y = df["innovation_score"]

    metrics_rows = []

    # 1. Regression model for final innovation score
    reg_model = RandomForestRegressor(n_estimators=120, random_state=42)

    if len(df) >= 10:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42
        )
        reg_model.fit(X_train, y_train)
        pred = reg_model.predict(X_test)

        mae = mean_absolute_error(y_test, pred)
        mse = mean_squared_error(y_test, pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, pred)

        metrics_rows.append({"model": "Random Forest Regressor", "metric": "MAE", "value": safe_round(mae)})
        metrics_rows.append({"model": "Random Forest Regressor", "metric": "MSE", "value": safe_round(mse)})
        metrics_rows.append({"model": "Random Forest Regressor", "metric": "RMSE", "value": safe_round(rmse)})
        metrics_rows.append({"model": "Random Forest Regressor", "metric": "R2 Score", "value": safe_round(r2)})

        print("Regression Evaluation")
        print("MAE:", round(mae, 2))
        print("MSE:", round(mse, 2))
        print("RMSE:", round(rmse, 2))
        print("R2 Score:", round(r2, 2))
    else:
        reg_model.fit(X, y)
        metrics_rows.append({"model": "Random Forest Regressor", "metric": "Note", "value": "Small dataset, trained on all data"})
        print("Regression model trained on all data because dataset is small.")

    joblib.dump(reg_model, os.path.join(MODEL_DIR, "innovation_model.pkl"))

    # 2. Classification model for Low / Medium / High level
    df["level"] = df["innovation_score"].apply(make_level)
    clf = RandomForestClassifier(n_estimators=120, random_state=42)

    if len(df) >= 12 and df["level"].nunique() > 1:
        X_train, X_test, y_train, y_test = train_test_split(
            X, df["level"], test_size=0.25, random_state=42, stratify=df["level"] if df["level"].value_counts().min() >= 2 else None
        )
        clf.fit(X_train, y_train)
        pred = clf.predict(X_test)

        acc = accuracy_score(y_test, pred)
        precision = precision_score(y_test, pred, average="weighted", zero_division=0)
        recall = recall_score(y_test, pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, pred, average="weighted", zero_division=0)

        metrics_rows.append({"model": "Random Forest Classifier", "metric": "Accuracy", "value": safe_round(acc)})
        metrics_rows.append({"model": "Random Forest Classifier", "metric": "Precision", "value": safe_round(precision)})
        metrics_rows.append({"model": "Random Forest Classifier", "metric": "Recall", "value": safe_round(recall)})
        metrics_rows.append({"model": "Random Forest Classifier", "metric": "F1 Score", "value": safe_round(f1)})

        print("\nClassification Evaluation")
        print("Accuracy:", round(acc, 2))
        print("Precision:", round(precision, 2))
        print("Recall:", round(recall, 2))
        print("F1 Score:", round(f1, 2))
    else:
        clf.fit(X, df["level"])
        metrics_rows.append({"model": "Random Forest Classifier", "metric": "Note", "value": "Small or single-class dataset, trained on all data"})
        print("Classification model trained on all data because dataset is small or has one class.")

    joblib.dump(clf, os.path.join(MODEL_DIR, "level_model.pkl"))

    # 3. KMeans clustering for thinking pattern groups
    cluster_count = 4 if len(df) >= 12 else 3
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features + ["innovation_score"]])
    km = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
    km.fit(X_scaled)

    joblib.dump(km, os.path.join(MODEL_DIR, "cluster_model.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

    df["cluster"] = km.labels_
    df.to_csv("data/attempts_with_clusters.csv", index=False)

    pd.DataFrame(metrics_rows).to_csv(os.path.join(RESULT_DIR, "model_metrics.csv"), index=False)

    print("\nTraining completed.")
    print("Saved model files in models folder.")
    print("Saved evaluation metrics in results/model_metrics.csv")
    print("Saved clustered data in data/attempts_with_clusters.csv")


if __name__ == "__main__":
    main()
