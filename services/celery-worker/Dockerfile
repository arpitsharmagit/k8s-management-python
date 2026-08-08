FROM python:3.12-slim

LABEL maintainer="iot-platform"
LABEL description="Celery Event Worker"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Start both the Celery worker and the Redis Pub/Sub subscriber
CMD ["sh", "-c", "celery -A app.celery_app worker --loglevel=info -Q telemetry,device_status,methods & python -m app.subscribers.redis_subscriber"]
