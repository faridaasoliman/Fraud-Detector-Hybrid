# backend/local_predict.py
import joblib
import pandas as pd

# Load your trained model
MODEL_PATH = "backend/models/model.pkl"
model_pipeline = joblib.load(MODEL_PATH)

# Example function to predict fraud
def predict_fraud(amount, time, country, merchant_category,
                  transaction_type, device, card_type, prev_fraud):
    # Put inputs in a DataFrame
    input_df = pd.DataFrame([{
        "Amount": amount,
        "Time": time,
        "Country": country,
        "Merchant_Category": merchant_category,
        "Transaction_Type": transaction_type,
        "Device": device,
        "Card_Type": card_type,
        "Previous_Fraud_History": prev_fraud
    }])

    # Predict probability and label
    prob = model_pipeline.predict_proba(input_df)[:, 1][0]
    label = int(prob >= 0.5)
    return {"probability": float(prob), "prediction": "Fraud" if label == 1 else "Not Fraud"}

# Example usage
if __name__ == "__main__":
    result = predict_fraud(
        amount=120.50,
        time=3600,
        country="USA",
        merchant_category="Electronics",
        transaction_type="Online",
        device="Mobile",
        card_type="Credit",
        prev_fraud=0
    )
    print(result)
