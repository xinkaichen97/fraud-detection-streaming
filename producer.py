import os
import time
import json
import random
from datetime import datetime
from confluent_kafka import Producer
from faker import Faker

KAFKA_TOPIC = "transactions"
faker = Faker()

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BROKER', 'localhost:9092')
producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})

def delivery_report(err, msg):
    """Callback for message delivery reports."""
    if err is not None:
        print(f'Message delivery failed: {err}')

def generate_transaction():
    """Generate synthetic transaction data with occasional fraud patterns."""
    user_id = random.randint(1000, 1010)

    is_fraud = random.random() > 0.95

    if is_fraud:
        amount = round(random.uniform(5000.00, 10000.00), 2)
        category = "Electronics"
    else:
        amount = round(random.uniform(5.00, 150.00), 2)
        category = faker.random_element(elements=('Groceries', 'Gas', 'Dining', 'Retail'))

    transaction = {
        "transaction_id": faker.uuid4(),
        "user_id": user_id,
        "amount": amount,
        "category": category,
        "timestamp": datetime.utcnow().isoformat(),
        "merchant_id": faker.uuid4()
    }
    return transaction

def main():
    print(f"🚀 Starting producer. Sending data to topic: {KAFKA_TOPIC}...")
    
    try:
        while True:
            # Generate synthetic data
            transaction = generate_transaction()
            
            value = json.dumps(transaction).encode('utf-8')

            # Key ensures all transactions for the same user go to the same partition
            producer.produce(
                topic=KAFKA_TOPIC,
                key=str(transaction['user_id']),
                value=value,
                callback=delivery_report
            )

            producer.flush()
            print(f"Sent: {transaction['amount']} | User: {transaction['user_id']}")
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nStopping producer...")
    finally:
        producer.flush()

if __name__ == "__main__":
    main()
