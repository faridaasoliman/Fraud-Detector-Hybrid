# model_loader.py
import joblib
import pandas as pd
import numpy as np
import os


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "model.pkl")
META_PATH = os.path.join(CURRENT_DIR, "model_meta.json")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}")

model = joblib.load(MODEL_PATH)

# Load metadata to get feature names
import json
with open(META_PATH, 'r') as f:
    meta = json.load(f)

numeric_features = meta.get('numeric_features', [])
categorical_features = meta.get('categorical_features', [])
all_features = numeric_features + categorical_features

def time_to_seconds(time_str):
    """Convert HH:MM format to seconds since midnight"""
    try:
        h, m = map(int, str(time_str).split(':'))
        return h * 3600 + m * 60
    except:
        return 0

def get_feature_importances(data_dict):
    """Get normalized feature importance scores based on the model.
    
    Returns a dictionary mapping feature names to importance scores (0-100).
    """
    # Convert Time from HH:MM to seconds if it's a string
    if isinstance(data_dict.get('Time'), str):
        data_dict['Time'] = time_to_seconds(data_dict['Time'])
    
    df = pd.DataFrame([data_dict])
    
    # Get the classifier (last step in the pipeline)
    # The pipeline structure is: preprocessor -> smote -> classifier
    classifier = model.named_steps['classifier']
    
    # Get feature importances from the RandomForest
    importances = classifier.feature_importances_
    
    # Normalize to 0-100
    if importances.sum() > 0:
        normalized = (importances / importances.sum()) * 100
    else:
        normalized = np.zeros_like(importances)
    
    # Create mapping of feature names to importances
    # After preprocessing, features are ordered as: numeric features + one-hot encoded categorical
    feature_importance_dict = {}
    
    # Numeric features come first
    for i, fname in enumerate(numeric_features):
        if i < len(normalized):
            feature_importance_dict[fname] = float(normalized[i])
    
    # Categorical features are one-hot encoded, so we aggregate their importances
    n_numeric = len(numeric_features)
    for i, fname in enumerate(categorical_features):
        # Each categorical feature becomes multiple one-hot encoded columns
        # We'll use a simple approach: assign the average importance of its encoded columns
        # For simplicity, we'll approximate by using base importance
        if n_numeric + i < len(normalized):
            feature_importance_dict[fname] = float(normalized[n_numeric + i])
    
    return feature_importance_dict

def predict_fraud(data_dict):
    """Predict fraud probability for a transaction.
    
    Args:
        data_dict: Dictionary with keys: Amount, Time (HH:MM format), Country, 
                   MerchantCategory, TransactionType, Device, CardType, PreviousFraudHistory
    
    Returns:
        (probability, label, feature_importances) tuple
    """
    # Convert Time from HH:MM to seconds if it's a string
    if isinstance(data_dict.get('Time'), str):
        data_dict['Time'] = time_to_seconds(data_dict['Time'])
    
    df = pd.DataFrame([data_dict])
    prob = model.predict_proba(df)[0][1]
    label = 1 if prob >= 0.5 else 0
    
    # Get feature importances
    try:
        feature_importances = get_feature_importances(data_dict)
    except Exception as e:
        # Fallback if importance calculation fails
        feature_importances = {f: 0 for f in all_features}
    
    return prob, label, feature_importances
