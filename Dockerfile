# Use a slim Python image
FROM python:3.12-slim

# Install system dependencies required for compiling Kafka/Feast/XGBoost
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Default command
CMD ["python", "prediction_service.py"]