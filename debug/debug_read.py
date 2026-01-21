# Create test_read.py
from feast import FeatureStore
fs = FeatureStore(repo_path="./feature_repo")

features = fs.get_online_features(
    features=["transaction_stats_fv:transaction_count_10m"],
    entity_rows=[{"user_id": "9999"}]
).to_dict()

print(features)
