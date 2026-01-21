import time
import pandas as pd
import numpy as np
import xgboost as xgb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from feast import FeatureStore

app = FastAPI()
fs = FeatureStore(repo_path="./feature_repo")

print("Loading model...")
model = xgb.XGBClassifier()
model.load_model("fraud_model.json")
print("Model loaded.")

class PredictionRequest(BaseModel):
    user_id: int

@app.post("/predict")
async def predict_fraud(request: PredictionRequest):
    start_time = time.time()

    try:
        features = fs.get_online_features(
            features=[
                "transaction_stats_fv:transaction_count_10m",
                "transaction_stats_fv:total_amount_10m",
                "user_credit_score_fv:credit_score"
            ],
            entity_rows=[{"user_id": request.user_id}]
        ).to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    feature_latency_ms = (time.time() - start_time) * 1000

    txn_count = features["transaction_count_10m"][0] or 0
    total_amt = features["total_amount_10m"][0] or 0.0
    credit_score = features["credit_score"][0] or 700

    input_vector = pd.DataFrame([{
        "transaction_count_10m": txn_count,
        "total_amount_10m": total_amt,
        "credit_score": credit_score
    }])

    fraud_prob = model.predict_proba(input_vector)[0][1]
    is_fraud = fraud_prob > 0.5

    total_latency_ms = (time.time() - start_time) * 1000

    return {
        "user_id": request.user_id,
        "prediction": "FRAUD" if is_fraud else "LEGIT",
        "probability": float(fraud_prob),
        "features": {
            "txn_count_10m": txn_count,
            "total_amount_10m": total_amt,
            "credit_score": credit_score
        },
        "latency_stats": {
            "feature_retrieval_ms": round(feature_latency_ms, 2),
            "total_latency_ms": round(total_latency_ms, 2)
        }
    }
