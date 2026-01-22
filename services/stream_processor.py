import json
import pandas as pd
import os
from kafka import KafkaConsumer
from feast import FeatureStore
from collections import defaultdict, deque
from datetime import datetime, timedelta

fs = FeatureStore(repo_path="./feature_repo")
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')

consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Maintain sliding window state per user (similar to Flink keyed state)
user_windows = defaultdict(lambda: deque())

def process_window(user_id, current_amount, event_timestamp):
    """Calculate streaming features using a 10-minute sliding window."""
    event_time = datetime.fromisoformat(event_timestamp)
    user_windows[user_id].append((event_time, current_amount))

    # Remove events outside the 10-minute window
    cutoff = event_time - timedelta(minutes=10)
    while user_windows[user_id] and user_windows[user_id][0][0] < cutoff:
        user_windows[user_id].popleft()

    count_10m = len(user_windows[user_id])
    total_amount_10m = sum(amt for _, amt in user_windows[user_id])

    return count_10m, total_amount_10m

def main():
    print("⚡ Stream Processor Started. Listening to Kafka...")
    
    for message in consumer:
        event = message.value
        user_id = event['user_id']
        amount = event['amount']
        timestamp = event['timestamp']

        count_10m, total_amount_10m = process_window(user_id, amount, timestamp)

        df = pd.DataFrame.from_dict({
            "user_id": [user_id],
            "event_timestamp": [datetime.fromisoformat(timestamp)],
            "transaction_count_10m": [count_10m],
            "total_amount_10m": [total_amount_10m],
        })

        try:
            fs.push("transaction_stats_push", df, to="online")
            print(f"✅ User {user_id}: Pushed to Redis successfully.")
        except Exception as e:
            print(f"❌ FAILED to push to Redis: {e}")

        print(f"User {user_id}: {count_10m} txns in last 10m. Pushed to Feature Store.")

if __name__ == "__main__":
    main()
