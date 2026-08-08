# Distributed IoT Hub and Kubernetes Fleet Management Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API%20Gateway-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Flask](https://img.shields.io/badge/Flask-Admin%20UI-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Celery](https://img.shields.io/badge/Celery-Worker%20Queue-37814A?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

Production-style Python platform for IoT telemetry, command orchestration, and Kubernetes operations visibility.
It combines async APIs, event-driven processing, MQTT transport, and a desktop control plane for real-time fleet operations.

## Project Highlights

- Async FastAPI gateway for authentication, devices, and telemetry workflows
- Celery worker pipeline with Redis pub/sub and broker-backed background processing
- MQTT-based telemetry transport using Eclipse Mosquitto
- Flask admin console for operational controls
- PySide6 desktop app for Kubernetes pods, deployments, logs, and cluster views
- Containerized local platform via Docker Compose

## Architecture

```mermaid
flowchart LR
	A[IoT Device] --> B[MQTT Broker - Mosquitto]
	B --> C[FastAPI Gateway]
	C --> D[(PostgreSQL)]
	C --> E[(Redis)]
	E --> F[Celery Worker]
	F --> D
	G[Flask Admin] --> C
	H[PySide6 Desktop App] --> I[Kubernetes API]
	H --> C
```

## Telemetry Workflow

```mermaid
sequenceDiagram
	participant Device as IoT Device
	participant MQTT as Mosquitto
	participant API as FastAPI
	participant Redis as Redis
	participant Worker as Celery Worker
	participant DB as PostgreSQL

	Device->>MQTT: Publish telemetry event
	MQTT->>API: Forward payload
	API->>Redis: Queue processing task
	Redis->>Worker: Dispatch task
	Worker->>DB: Persist and update status
	API-->>Device: ACK / response
```

## Visual Showcase

The docs/images folder now contains reusable visual assets for GitHub portfolio presentation.

### Architecture Board

![Architecture Board](docs/images/architecture-board.svg)

### Workflow Board

![Workflow Board](docs/images/workflow-board.svg)

### Feature Cards

![Feature Cards](docs/images/feature-cards.svg)

### App Screenshot Placeholders

![FastAPI Swagger UI ](docs/images/fastapi-docs.png)
![Flask Admin Dashboard ](docs/images/flask-admin-dashboard.png)
![Desktop Cluster Monitor ](docs/images/desktop-cluster-panel.png)
![Flask Admin Devices ](docs/images/admin-dashboard.png)

## Repository Layout

```text
.
├── infra/
│   ├── mosquitto/
│   └── postgres/
├── services/
│   ├── fastapi-gateway/
│   ├── flask-admin/
│   ├── celery-worker/
│   └── desktop-app/
├── docker-compose.yml
└── run.sh
```

## Technologies Used

- Language: Python 3.11+
- API and Web: FastAPI, Uvicorn, Flask
- Messaging and Async: MQTT (Paho), Celery, Redis
- Database: PostgreSQL, SQLAlchemy, Alembic
- Desktop: PySide6, Kubernetes Python Client
- Infrastructure: Docker, Docker Compose
- Security and Auth: JWT (`python-jose`), `passlib`

## Quick Start

### 1. Clone repository

```bash
git clone git@github.com:arpitsharmagit/k8s-management-python.git
cd k8s-management-python
```

### 2. Start full platform (Docker)

```bash
chmod +x run.sh
./run.sh stack
```

### 3. Access services

- FastAPI docs: http://localhost:8000/docs
- Flask admin: http://localhost:5000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- MQTT: localhost:1883

## Local Development Modes

```bash
./run.sh fastapi
./run.sh flask
./run.sh worker
./run.sh desktop
```
