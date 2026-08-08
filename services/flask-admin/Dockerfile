FROM python:3.12-slim

LABEL maintainer="iot-platform"
LABEL description="Flask Admin Web UI"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app
ENV FLASK_ENV=production

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:create_app()"]

EXPOSE 5000
