# Project Structure

This document describes the organization of the fraud detection streaming project.

## Directory Layout

```
fraud-detection-streaming/
│
├── models/                     # ML Models & Training
│   ├── __init__.py
│   ├── train_model.py          # XGBoost model training script
│   └── fraud_model.json        # Trained model artifact
│
├── services/                   # Microservices
│   ├── __init__.py
│   ├── producer.py             # Kafka transaction generator
│   ├── stream_processor.py     # Real-time feature engineering
│   └── prediction_service.py   # FastAPI prediction endpoint
│
├── scripts/                    # Setup & Initialization
│   ├── __init__.py
│   ├── init_db.py             # Database initialization (local)
│   └── init_feast.py          # Feast setup (Docker)
│
├── feature_repo/               # Feast Feature Store
│   ├── features.py            # Feature definitions
│   ├── feature_store_docker.yaml
│   └── feature_store_local.yaml
│
├── debug/                      # Debug utilities
│   ├── debug_check_connection.py
│   ├── debug_diagnose_feast.py
│   ├── debug_push.py
│   └── debug_read.py
│
├── docker-compose.yml          # Container orchestration
├── Dockerfile                  # Application container
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project metadata
└── README.md                  # Main documentation

```

## Component Responsibilities

### Models (`models/`)
- **train_model.py**: Trains XGBoost classifier on synthetic fraud data
- **fraud_model.json**: Serialized model used by prediction service

### Services (`services/`)
- **producer.py**: Generates synthetic transaction events to Kafka
- **stream_processor.py**: Consumes Kafka events, calculates sliding window features, pushes to Feast
- **prediction_service.py**: FastAPI server that retrieves features from Feast and serves predictions

### Scripts (`scripts/`)
- **init_db.py**: Creates PostgreSQL tables and populates with sample data (local development)
- **init_feast.py**: Initializes Feast feature store in Docker environment

### Feature Repo (`feature_repo/`)
- **features.py**: Defines Feast entities, sources, and feature views
- **feature_store_*.yaml**: Feast configuration for different environments

## Running Components

### Train Model
```bash
python models/train_model.py
```

### Run Services Locally
```bash
# Producer
python services/producer.py

# Stream Processor
python services/stream_processor.py

# Prediction API
uvicorn services.prediction_service:app --reload
```

### Run with Docker Compose
```bash
docker-compose up
```

## Notes
- All services run from the project root directory
- Paths in code use relative paths from root (e.g., `./models/fraud_model.json`)
- Docker containers maintain the same directory structure
