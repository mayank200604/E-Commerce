# E-commerce: Amazon Product Quality Predictor

An end-to-end, production-quality weakly supervised machine learning pipeline that predicts product quality levels (Low / Medium / High) for approximately 75,000 real-world e-commerce products using structured reasoning and NLP.

## Project Overview

The **Amazon Product Quality Predictor** tackles the fundamental challenge of building supervised machine learning models without ground-truth labels. The dataset contains `catalog_content` (text), `price`, and `image_link`, with no ground-truth quality labels provided. 

Using a **weak supervision** approach, quality labels were engineered by aggregating observable signals:
- **Text Richness:** Evaluated through character length and word count percentiles.
- **Price Sanity:** Utilized Interquartile Range (IQR)-based outlier detection.
- **Price–Text Consistency:** Scored the alignment between product pricing and description richness.
- **Aggregated Scoring Logic:** A weighted numerical composite score mapped to a final `quality_label` ∈ `{0: Low, 1: Medium, 2: High}`.

## System Architecture

The pipeline is designed to move systematically from raw data directly to a deployable web application:

```text
Dataset
   ↓
Weak Label Engineering
   ↓
TF-IDF + Structured Features
   ↓
Model Training & Evaluation
   ↓
Model Serialization (.pkl)
   ↓
FastAPI Backend
   ↓
Dashboard + Visualization Engine
```

## Feature Engineering & Modeling

### Feature Engineering
Our engineered feature space utilizes both textual and continuous numeric inputs:
- **NLP Features:** TF-IDF vectorization with **40,000 features** (unigrams + bigrams), stripped of English stopwords.
- **Structured Features:** Scaled continuous price inputs, price outlier flags, consistency scores, and content richness metrics.
- **Reproducibility:** All preprocessing artifacts (`tfidf_vectorizer`, `price_scaler`) are serialized for reproducible inference.

### Model Benchmarking & Validation
We benchmarked several models, including:
- **Logistic Regression (class-balanced)**
- **Decision Tree**
- **Random Forest**
- **LightGBM**

Validation was performed using a **stratified 80/20 split** (~15,000 validation samples). 

**Final Selected Model:** **Logistic Regression (class-balanced)** achieved a **Macro F1 ≈ 0.82**, demonstrating highly stable multi-class separation performance.

### ResNet-50 Image Embedding Experiment
During early iteration, a multimodal experiment was conducted to extract pretrained visual embeddings using **ResNet-50**, which were then combined with structured features. However, empirical testing showed an early performance saturation (Macro F1 plateaued around 0.64). The image pathway was systematically removed to optimize computational overhead, demonstrating strong **cost-benefit evaluation discipline**.

## Natural-Language Visualization Engine

The project includes an intelligent, natural-language-driven analytics visualization engine. Users can input conversational queries like:
- *"Show distribution of high-quality products"*
- *"Compare average price across quality levels"*

The system will parse these queries and dynamically map them to predefined Matplotlib visualization logic, automatically returning visual charts directly onto the dashboard.

## Project Structure

```text
E-Commerce/
├── app/
│   ├── main.ipynb                    # Jupyter notebook for exploratory data analysis
│   ├── train.ipynb                   # Experimental notebook for model training
│   ├── main.py                       # Core training pipeline script
│   ├── api.py                        # FastAPI microservice for raw model triggering
│   ├── dashboard_api.py              # Main FastAPI backend routing and visualization endpoint
│   ├── visualization.py              # Natural-language visualization engine
│   ├── dashboard.html                # Frontend user interface dashboard
│   ├── dashboard.css                 # Frontend styling
│   ├── dashboard.js                  # Frontend interactive logic
│   ├── tfidf_vectorizer.pkl          # Serialized NLP feature extractor
│   ├── price_scaler.pkl              # Serialized numeric feature scaler
│   ├── model_logistic_regression.pkl # Serialized production model
│   ├── requirements.txt              # Environment dependencies
│   ├── train.csv                     # Raw e-commerce product dataset
│   ├── train_with_quality_label.csv  # Dataset enriched with engineered quality labels
│   └── README.md                     # Existing project documentation
```

## Installation & Usage

### 1. Clone the repository
```bash
git clone https://github.com/mayank200604/E-Commerce.git
cd E-Commerce/app
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*Core Libraries used:* `numpy`, `pandas`, `scikit-learn`, `matplotlib`, `lightgbm`, `fastapi`, `uvicorn`, `joblib`.

### 4. Application Execution

**To train the model from scratch:**
```bash
python main.py
```

**To start the original FastAPI server:**
```bash
uvicorn api:app --reload
```

**To start the dashboard backend endpoint:**
```bash
uvicorn dashboard_api:app --reload
```
Once deployed, navigate your browser to `http://localhost:8000/dashboard` to access the main interface.

## Deployment

The backend application is fully prepared for fast production environments. The system is structurally prepared for backend deployment on **Render**, exposing a **REST API-based inference endpoint** and public dashboard access over HTTP reliably.

**Live Deployment:** [https://churn-prediction-qq8x.onrender.com]

## Key Highlights

- **Weak Supervision Mastery:** Conversion of a completely unlabeled dataset of ~75,000 samples into a structured supervised ML problem.
- **Structured Validation Methodology:** Maintained extreme rigor using strict stratified splits and robust algorithmic benchmarking.
- **Cost-Aware Experimentation:** ResNet-50 visual feature evaluation combined with intentional deprecation for greater deployment runtime efficiency.
- **Deployment-Ready Architecture:** Clean separation of concerns from model training scripts to dynamic FastAPI endpoints.
- **Visualization-Driven Analytics:** Real-time translation of natural language queries directly into graphical, actionable Matplotlib insights.

## Future Improvements

- **SHAP Explainability:** Introduce SHapley Additive exPlanations to interpret feature importance on a per-prediction level.
- **Cross-Validation Hyperparameter Tuning:** Integrate K-Fold validation paired with Optuna or GridSearchCV.
- **Docker Containerization:** Create Docker container specifications to cleanly bundle the API and frontend assets, guaranteeing environment parity.
- **Real-Time Image Embedding Microservice:** Orchestrating an independent ResNet backend running under an event-driven framework.
- **CI/CD Integration:** Leveraging standard GitHub Actions workflows to govern, lint, and autonomously deploy iterations.
