from feast import FeatureStore
import pandas as pd
from datetime import datetime, timezone

fs = FeatureStore(repo_path="./feature_repo")

# --- DEBUGGING TYPES ---
# We force user_id to be an Integer first (int64)
# If this fails, we will try casting it to str() in the next run.
user_id_value = "9999" 

print(f"🛠 Preparing test data for User ID: {user_id_value} (Type: {type(user_id_value)})")

df = pd.DataFrame({
    "user_id": [user_id_value],
    "event_timestamp": [datetime.now(timezone.utc)],
    "transaction_count_10m": [50],
    "total_amount_10m": [1234.56]
})

# EXPLICITLY cast to correct types to avoid Pandas inference issues
df['user_id'] = df['user_id'].astype('str') 
df['transaction_count_10m'] = df['transaction_count_10m'].astype('int64')
df['total_amount_10m'] = df['total_amount_10m'].astype('float32')

print("DataFrame Dtypes:")
print(df.dtypes)

try:
    print("🚀 Pushing to Feature Store...")
    fs.push("transaction_stats_push", df, to="online")
    print("✅ Push command executed.")
except Exception as e:
    print(f"❌ Push FAILED: {e}")

# Immediate Retrieval Test
print("🔎 Attempting immediate retrieval...")
features = fs.get_online_features(
    features=["transaction_stats_fv:transaction_count_10m"],
    entity_rows=[{"user_id": user_id_value}]
).to_dict()

print("Result:", features)