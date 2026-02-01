# Cerberus: Real-Time Fraud Detection System

A production-grade streaming fraud detection pipeline that processes transactions in real-time with sub-10ms latency. Built with Kafka, Feast feature store, and XGBoost for high-performance ML inference.

## Overview

This system demonstrates a modern MLOps architecture for real-time fraud detection, featuring:

- **Streaming Feature Engineering**: Sliding window aggregations over Kafka streams
- **Feature Store Integration**: Feast for consistent online/offline feature serving
- **Low-Latency Inference**: Redis-backed online feature store for <10ms predictions
- **Containerized Deployment**: Docker Compose orchestration for local development

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Producer   │────▶│    Kafka     │────▶│  Processor  │
│ (Synthetic) │     │ (Streaming)  │     │  (Features) │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                                                 ▼
                    ┌──────────────┐     ┌─────────────┐
                    │  Prediction  │◀────│    Feast    │
                    │     API      │     │ Feature Store│
                    └──────────────┘     └─────────────┘
                                         │             │
                                    Redis (Online) Postgres (Offline)
```

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Message Broker** | Kafka | Stream transaction events |
| **Stream Processor** | Python | Calculate sliding window features |
| **Feature Store** | Feast | Manage online/offline features |
| **Online Store** | Redis | Sub-10ms feature retrieval |
| **Offline Store** | PostgreSQL | Historical feature storage |
| **ML Model** | XGBoost | Fraud classification |
| **API** | FastAPI | Serve predictions |

## Project Structure

```
fraud-detection-streaming/
├── docker-compose.yml          # Service orchestration
├── Dockerfile                  # Application container
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
│
├── services/                  # Microservices
│   ├── producer.py            # Kafka transaction generator
│   ├── stream_processor.py    # Feature engineering pipeline
│   └── prediction_service.py  # FastAPI prediction endpoint
│
├── models/                    # ML models
│   ├── train_model.py         # Model training script
│   └── fraud_model.json       # Trained XGBoost model
│
├── scripts/                   # Setup and initialization
│   ├── init_feast.py          # Feature store initialization
│   └── init_db.py             # Database setup (local)
│
├── feature_repo/              # Feast feature definitions
│   ├── features.py            # Feature definitions
│   ├── feature_store_docker.yaml   # Feast config (Docker)
│   └── feature_store_local.yaml    # Feast config (local)
│
└── debug/                     # Debug utilities
```

## Features

### Streaming Features (10-minute sliding window)
- `transaction_count_10m`: Number of transactions in last 10 minutes
- `total_amount_10m`: Total transaction amount in last 10 minutes

### Batch Features
- `credit_score`: User credit score (30-day TTL)

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fraud-detection-streaming
   ```

2. **Start the entire stack**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Launch Kafka, Redis, PostgreSQL
   - Initialize the Feast feature registry
   - Start the producer, processor, and API services

3. **Test the prediction API**
   ```bash
   curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1005}'
   ```

   **Example Response:**
   ```json
   {
     "user_id": 1005,
     "prediction": "LEGIT",
     "probability": 0.12,
     "features": {
       "txn_count_10m": 2,
       "total_amount_10m": 127.50,
       "credit_score": 720
     },
     "latency_stats": {
       "feature_retrieval_ms": 4.23,
       "total_latency_ms": 8.91
     }
   }
   ```

### Service Endpoints

| Service | Port | Description |
|---------|------|-------------|
| FastAPI | 8000 | Prediction API |
| Kafdrop | 9000 | Kafka UI for monitoring |
| Kafka | 9092 | Message broker |
| PostgreSQL | 5432 | Offline feature store |
| Redis | 6379 | Online feature store |

## Local Development

### Setup Python Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Train the Model

```bash
python models/train_model.py
```

This generates `models/fraud_model.json` with synthetic training data.

### Initialize Feature Store (Local)

```bash
cd feature_repo
feast apply
```

### Run Components Individually

```bash
# Start producer (requires Kafka running)
python services/producer.py

# Start stream processor (requires Kafka, Redis, PostgreSQL)
python services/stream_processor.py

# Start API (requires Redis, PostgreSQL, trained model)
uvicorn services.prediction_service:app --reload
```

## How It Works

### 1. Data Generation
The producer generates synthetic transaction events with occasional fraud patterns:
- Normal: 5-150 USD transactions
- Fraud: 5000-10000 USD transactions (5% of traffic)

### 2. Stream Processing
The processor consumes Kafka events and:
1. Maintains a 10-minute sliding window per user
2. Calculates aggregate features (count, sum)
3. Pushes features to Feast online store (Redis)

### 3. Real-Time Inference
The API receives prediction requests and:
1. Fetches features from Redis (<10ms)
2. Runs XGBoost inference
3. Returns fraud probability and features

## Configuration

### Docker Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KAFKA_BROKER` | `kafka:29092` | Kafka bootstrap servers |

### Feature Store Configuration

See [`feature_repo/feature_store_docker.yaml`](feature_repo/feature_store_docker.yaml) for Feast configuration.

## Monitoring

### Kafka UI (Kafdrop)
Access Kafdrop at `http://localhost:9000` to:
- View topic messages
- Monitor consumer lag
- Inspect partition distribution

### Logs
View service logs:
```bash
docker-compose logs -f [service-name]
# Examples: producer, processor, api
```

## Performance Metrics

- **Feature Retrieval Latency**: ~4-6ms (Redis lookup)
- **Total Prediction Latency**: ~8-12ms (end-to-end)
- **Throughput**: 100+ predictions/second (single instance)

## Production Considerations

For production deployment, consider:

1. **Security**
   - Use secrets management (not hardcoded credentials)
   - Enable TLS/SSL for Kafka and Redis
   - Implement authentication for API endpoints

2. **Scalability**
   - Deploy multiple processor instances with Kafka consumer groups
   - Use managed Kafka (AWS MSK, Confluent Cloud)
   - Redis cluster for high availability

3. **Monitoring**
   - Add Prometheus/Grafana for metrics
   - Implement distributed tracing (OpenTelemetry)
   - Set up alerting for model drift

4. **Model Management**
   - Version models with MLflow or similar
   - Implement A/B testing framework
   - Monitor prediction accuracy in production

## Technology Stack

- **Languages**: Python 3.12
- **ML Framework**: XGBoost, scikit-learn
- **Feature Store**: Feast
- **Message Queue**: Apache Kafka (Confluent)
- **Databases**: Redis, PostgreSQL
- **API Framework**: FastAPI
- **Containerization**: Docker, Docker Compose

## License

MIT License

## Contributing

Contributions welcome! Please submit a pull request or open an issue for discussion.
