import os
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

FEATURE_COLUMNS = [
    "distance_from_home",
    "distance_from_last_transaction",
    "ratio_to_median_purchase_price",
    "repeat_retailer",
    "used_chip",
    "used_pin_number",
    "online_order",
]

def load_data():
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "card_transdata.csv")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows, fraud rate: {df['fraud'].mean():.4%}")
    return df

def train():
    print("Loading Kaggle Credit Card Fraud dataset...")
    df = load_data()

    X = df[FEATURE_COLUMNS]
    y = df["fraud"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    n_legit = (y_train == 0).sum()
    n_fraud = (y_train == 1).sum()
    print(f"Training set: {n_legit} legit, {n_fraud} fraud")

    print("Training XGBoost model...")
    model = xgb.XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        use_label_encoder=False,
        n_estimators=100,
        max_depth=6,
        scale_pos_weight=n_legit / max(n_fraud, 1),
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\nModel Performance:")
    print(classification_report(y_test, y_pred))

    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_filename = os.path.join(model_dir, "fraud_model.json")
    model.save_model(model_filename)
    print(f"Model saved to {model_filename}")

if __name__ == "__main__":
    train()
