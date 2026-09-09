FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python ML dependencies
COPY ml/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend /app/backend
COPY ml /app/ml

ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "ml.serving.api:app", "--host", "0.0.0.0", "--port", "8001"]
