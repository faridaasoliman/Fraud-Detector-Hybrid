# train_model.py
# Usage:
# python backend/models/train_model.py

import os
import joblib
import json
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_PATH = os.path.join(PROJECT_ROOT, "backend", "data", "main.csv")
OUTPUT_MODEL_PATH = os.path.join(PROJECT_ROOT, "backend", "models", "model.pkl")
OUTPUT_META_PATH = os.path.join(PROJECT_ROOT, "backend", "models", "model_meta.json")

RANDOM_STATE = 42
TEST_SIZE = 0.2
# ----------------------------

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

def load_data(path):
    df = pd.read_csv(path)
    return df

def preprocess_and_train(df):
    """Preprocess the dataframe and train a model.

    This function will try to detect the target column automatically by checking
    common target names and then falling back to finding a binary column.
    """

    def detect_target_column(df):
        common = [
            "Class", "class", "IsFraud", "is_fraud", "Is_Fraud",
            "Label", "label", "Target", "target", "fraud", "Fraud"
        ]
        for c in common:
            if c in df.columns:
                return c

        # fallback: find any column with exactly two unique values (binary)
        for col in df.columns:
            try:
                unique = df[col].dropna().unique()
            except Exception:
                continue
            if len(unique) == 2:
                return col
        return None

    target_col = detect_target_column(df)
    if target_col is None:
        raise KeyError(
            "Could not detect a binary target column automatically. "
            f"Available columns: {list(df.columns)}"
        )

    print(f"Using target column: {target_col}")

    # Convert target to 0/1 integers if possible
    y_vals = pd.to_numeric(df[target_col], errors="coerce")
    if set(y_vals.dropna().unique()) <= {0, 1}:
        df[target_col] = y_vals.fillna(0).astype(int)
    else:
        # try mapping common string labels
        mapping = {
            "yes": 1, "no": 0, "true": 1, "false": 0,
            "y": 1, "n": 0, "fraud": 1, "legit": 0, "genuine": 0
        }
        mapped = df[target_col].astype(str).str.strip().str.lower().map(mapping)
        if set(mapped.dropna().unique()) <= {0, 1}:
            df[target_col] = mapped.fillna(0).astype(int)
        else:
            raise ValueError(
                f"Target column '{target_col}' could not be coerced to binary 0/1."
            )

    # Determine numeric vs categorical features automatically
    numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
    if target_col in numeric_features:
        numeric_features.remove(target_col)

    categorical_features = [c for c in df.columns if c not in numeric_features and c != target_col]

    # Convert Time from HH:MM format to seconds since midnight if needed
    if 'Time' in df.columns and df['Time'].dtype == 'object':
        def time_to_seconds(time_str):
            try:
                h, m = map(int, str(time_str).split(':'))
                return h * 3600 + m * 60
            except:
                return 0
        df['Time'] = df['Time'].apply(time_to_seconds)
        # Re-detect numeric features after conversion
        numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in numeric_features:
            numeric_features.remove(target_col)
        categorical_features = [c for c in df.columns if c not in numeric_features and c != target_col]

    # Ensure categorical fields are strings
    for c in categorical_features:
        df[c] = df[c].astype(str)

    # Split dataset
    X = df[numeric_features + categorical_features]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    # Build preprocessing pipelines
    numeric_transformer = Pipeline(steps=[("scaler", StandardScaler())])

    try:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)

    categorical_transformer = Pipeline(steps=[("onehot", ohe)])

    preprocessor = ColumnTransformer(transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ])

    # Classifier + SMOTE
    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

    smote = SMOTE(random_state=RANDOM_STATE)

    pipeline = ImbPipeline(steps=[
        ("preprocessor", preprocessor),
        ("smote", smote),
        ("classifier", clf)
    ])

    # Train
    print("Training model with SMOTE oversampling...")
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    # Some classifiers may not implement predict_proba for all cases; guard it
    try:
        y_prob = pipeline.predict_proba(X_test)[:, 1]
    except Exception:
        y_prob = None

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, y_prob)) if y_prob is not None else None,
    }

    print("Metrics:", metrics)
    print("\nClassification report:\n", classification_report(y_test, y_pred, digits=4))
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred))

    # Save model and metadata
    os.makedirs(os.path.dirname(OUTPUT_MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, OUTPUT_MODEL_PATH)

    meta = {
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "metrics": metrics,
        "random_state": RANDOM_STATE,
        "target_column": target_col
    }

    with open(OUTPUT_META_PATH, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nSaved model to {OUTPUT_MODEL_PATH}")
    print(f"Saved metadata to {OUTPUT_META_PATH}")

    return pipeline, meta

def main():
    print("Loading dataset...")
    df = load_data(DATA_PATH)
    preprocess_and_train(df)
    print("Done.")

if __name__ == "__main__":
    main()
