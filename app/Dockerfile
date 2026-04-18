FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run from /app root using module syntax so relative paths (../data, ../frontend) resolve correctly
CMD python -m uvicorn backend.dashboard_api:app --host 0.0.0.0 --port ${PORT:-10000}