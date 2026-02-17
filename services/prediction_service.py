import time
import xgboost as xgb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from feast import FeatureStore

app = FastAPI()
fs = FeatureStore(repo_path="./feature_repo")

FEATURE_COLUMNS = [
    "distance_from_home",
    "distance_from_last_transaction",
    "ratio_to_median_purchase_price",
    "repeat_retailer",
    "used_chip",
    "used_pin_number",
    "online_order",
]

FEAST_FEATURE_REFS = [f"transaction_stats_fv:{col}" for col in FEATURE_COLUMNS]

print("Loading model...")
model = xgb.Booster()
model.load_model("./models/fraud_model.json")
print("Model loaded.")

class PredictionRequest(BaseModel):
    user_id: int

@app.post("/predict")
async def predict_fraud(request: PredictionRequest):
    start_time = time.time()

    try:
        features = fs.get_online_features(
            features=FEAST_FEATURE_REFS,
            entity_rows=[{"user_id": request.user_id}]
        ).to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    feature_latency_ms = (time.time() - start_time) * 1000

    feature_values = []
    feature_dict = {}
    for col in FEATURE_COLUMNS:
        val = features[col][0]
        if val is None:
            val = 0.0
        feature_values.append(float(val))
        feature_dict[col] = val

    input_vector = xgb.DMatrix([feature_values], feature_names=FEATURE_COLUMNS)

    fraud_prob = model.predict(input_vector)[0]
    is_fraud = fraud_prob > 0.5

    total_latency_ms = (time.time() - start_time) * 1000

    return {
        "user_id": request.user_id,
        "prediction": "FRAUD" if is_fraud else "LEGIT",
        "probability": float(fraud_prob),
        "features": feature_dict,
        "latency_stats": {
            "feature_retrieval_ms": round(feature_latency_ms, 2),
            "total_latency_ms": round(total_latency_ms, 2)
        }
    }
