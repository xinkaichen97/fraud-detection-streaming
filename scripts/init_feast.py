#!/usr/bin/env python3
"""
Initialize Feast feature store and database for Docker environment.
This script should run once before starting the main services.
"""
import os
import sys
import time
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def wait_for_postgres(db_url, max_retries=30, delay=2):
    """Wait for PostgreSQL to be ready."""
    print(f"⏳ Waiting for PostgreSQL to be ready...")
    for i in range(max_retries):
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL is ready!")
            return engine
        except (OperationalError, Exception) as e:
            if i < max_retries - 1:
                print(f"   PostgreSQL not ready yet, retrying ({i+1}/{max_retries})...")
                time.sleep(delay)
            else:
                print(f"❌ PostgreSQL connection timeout! Error: {e}")
                sys.exit(1)

def init_db_tables(engine):
    """Initialize database tables with sample data."""
    print("\n⏳ Creating database tables...")

    # Table 1: Credit Scores
    print("   Creating 'user_credit_scores'...")
    credit_data = []
    for user_id in range(1000, 1011):
        credit_data.append({
            "user_id": user_id,
            "credit_score": 650 + (user_id % 10) * 20,
            "event_timestamp": datetime.now()
        })
    df_credit = pd.DataFrame(credit_data)
    df_credit.to_sql('user_credit_scores', engine, index=False, if_exists='replace')

    # Table 2: Transaction Stats
    print("   Creating 'transaction_stats'...")
    stats_data = []
    for user_id in range(1000, 1011):
        stats_data.append({
            "user_id": user_id,
            "transaction_count_10m": 0,
            "total_amount_10m": 0.0,
            "distance_from_home": 0.0,
            "distance_from_last_transaction": 0.0,
            "ratio_to_median_purchase_price": 0.0,
            "repeat_retailer": 0,
            "used_chip": 0,
            "used_pin_number": 0,
            "online_order": 0,
            "event_timestamp": datetime.now()
        })
    df_stats = pd.DataFrame(stats_data)
    df_stats.to_sql('transaction_stats', engine, index=False, if_exists='replace')

    print("✅ Database tables created!")

def apply_feast_features():
    """Apply Feast feature definitions."""
    print("\n⏳ Applying Feast feature definitions...")

    # Change to feature_repo directory
    os.chdir('/app/feature_repo')

    # Run feast apply
    exit_code = os.system('feast apply')

    if exit_code == 0:
        print("✅ Feast features applied successfully!")
    else:
        print("❌ Failed to apply Feast features!")
        sys.exit(1)

def main():
    print("=" * 60)
    print("🚀 Initializing Fraud Detection System")
    print("=" * 60)

    # Database connection string for Docker
    db_url = 'postgresql://user:password@postgres:5432/fraud_detection'

    # Wait for PostgreSQL and get connection
    engine = wait_for_postgres(db_url)

    # Initialize database tables
    init_db_tables(engine)

    # Apply Feast features
    apply_feast_features()

    print("\n" + "=" * 60)
    print("✅ Initialization complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
