# 1. Stable Python version (important)
FROM python:3.9-slim

# 2. Set working directory inside container
WORKDIR /app

# 3. Copy dependency list first
COPY requirements.txt .

# 4. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy main script
COPY main.py .
COPY api.py .

# 6. Copy pre-trained model artifacts
COPY model_logistic_regression.pkl .
COPY tfidf_vectorizer.pkl .
COPY price_scaler.pkl .


# 7. Copy data files
# This will:
#   - Load train.csv
#   - Generate quality labels
#   - Train the model
#   - Save artifacts
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000
