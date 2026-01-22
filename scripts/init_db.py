import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta

db_connection_str = 'postgresql://user:password@localhost:5432/fraud_detection'
db_connection = create_engine(db_connection_str)

def init_db():
    print("⏳ Generating historical data...")

    print("   Creating 'user_credit_scores'...")
    credit_data = []
    for user_id in range(1000, 1011):
        credit_data.append({
            "user_id": user_id,
            "credit_score": 650 + (user_id % 10) * 20,
            "event_timestamp": datetime.now()
        })
    df_credit = pd.DataFrame(credit_data)
    df_credit.to_sql('user_credit_scores', db_connection, index=False, if_exists='replace')

    print("   Creating 'transaction_stats'...")
    stats_data = []
    for user_id in range(1000, 1011):
        stats_data.append({
            "user_id": user_id,
            "transaction_count_10m": 0,
            "total_amount_10m": 0.0,
            "event_timestamp": datetime.now()
        })
    df_stats = pd.DataFrame(stats_data)
    df_stats.to_sql('transaction_stats', db_connection, index=False, if_exists='replace')

    print("✅ Success! Both tables created.")

if __name__ == "__main__":
    init_db()