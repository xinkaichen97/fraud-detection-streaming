import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

def generate_training_data(n_samples=5000):
    """
    Generates a synthetic dataset mimicking our Feast features:
    - transaction_count_10m (Streaming)
    - total_amount_10m (Streaming)
    - credit_score (Batch)
    - is_fraud (Target)
    """
    np.random.seed(42)
    
    # 1. Generate benign traffic (Normal behavior)
    # Low counts, low amounts, varying credit scores
    n_legit = int(n_samples * 0.90)
    legit_df = pd.DataFrame({
        "transaction_count_10m": np.random.poisson(2, n_legit),
        "total_amount_10m": np.random.exponential(50, n_legit),
        "credit_score": np.random.normal(700, 50, n_legit),
        "is_fraud": 0
    })

    # 2. Generate fraud traffic (Anomalous behavior)
    # High counts OR high amounts
    n_fraud = n_samples - n_legit
    fraud_df = pd.DataFrame({
        "transaction_count_10m": np.random.poisson(8, n_fraud),      # High frequency
        "total_amount_10m": np.random.exponential(5000, n_fraud),   # High amount
        "credit_score": np.random.normal(600, 80, n_fraud),         # Lower credit
        "is_fraud": 1
    })

    # Combine and shuffle
    df = pd.concat([legit_df, fraud_df]).sample(frac=1).reset_index(drop=True)
    return df

def train():
    print("🧠 Generating synthetic training data...")
    df = generate_training_data()
    
    # Features (X) and Target (y)
    X = df[["transaction_count_10m", "total_amount_10m", "credit_score"]]
    y = df["is_fraud"]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    # Train XGBoost
    print("🏋️ Training XGBoost model...")
    model = xgb.XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        use_label_encoder=False
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    print("\nModel Performance:")
    print(classification_report(y_test, y_pred))
    
    # Save Model
    model_filename = "fraud_model.json"
    model.save_model(model_filename)
    print(f"✅ Model saved to {model_filename}")

if __name__ == "__main__":
    train()
    