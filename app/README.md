# Amazon Product Quality Prediction System

> From Model to ML System — Understanding Product Quality at Scale

---

## Overview

This project transitions from building basic isolated ML models to developing a **complete, integrated ML system** that evaluates and predicts e-commerce product quality at scale.

Instead of relying on expensive manual labeling, the system uses **weakly supervised learning** — engineering proxy quality labels from observable signals in the raw data. A live analytical dashboard and landing page complete the full ML system experience.

---

## Problem Statement

> **How can we automatically assess the quality of product listings when explicit quality labels do not exist?**

This mirrors real production settings where:
- Labels are unavailable or expensive
- Quality must be inferred from indirect signals
- Decisions must be justified with data, not assumptions

---

## Project Structure

```
app/
├── backend/
│   ├── dashboard_api.py     ← Main FastAPI server (serves landing + dashboard)
│   ├── main.py              ← ML pipeline: weak labels + model training
│   ├── api.py               ← Utility FastAPI endpoint
│   └── visualization.py     ← Standalone query-based chart generator
│
├── frontend/
│   ├── landing.html         ← Project landing page (served at /)
│   ├── landing.css          ← Landing page styles (dark mode, glassmorphism)
│   ├── dashboard.html       ← Product Quality Dashboard (served at /dashboard)
│   ├── dashboard.css        ← Dashboard styles
│   └── dashboard.js         ← Dashboard interactivity & API calls
│
├── models/
│   ├── model_logistic_regression.pkl
│   ├── tfidf_vectorizer.pkl
│   └── price_scaler.pkl
│
├── data/
│   ├── train.csv                       ← Raw dataset (not committed, ~73MB)
│   └── train_with_quality_label.csv    ← Generated labeled dataset (~75k rows)
│
├── notebooks/
│   ├── main.ipynb           ← EDA & weak label engineering
│   └── train.ipynb          ← Feature extraction, modeling & evaluation
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Dataset

**~75,000 product listings** containing:
- `catalog_content` — full product description text
- `price` — product price
- `image_link` — URL to product image

A test file exists but is **not used** due to missing price data and absent labels.

---

## Step 1: Weak Label Engineering

Since no ground-truth labels exist, a **3-class quality label** was engineered from observable signals:

| Label | Class | Meaning |
|---|---|---|
| `0` | Low | Short descriptions, price anomalies |
| `1` | Medium | Average content, minor inconsistencies |
| `2` | High | Rich descriptions, consistent pricing |

### Label construction:
1. **Text quality score** — word-count percentiles (25th / 75th)
2. **Price sanity score** — IQR-based outlier detection
3. **Price–text consistency score** — word count vs price bin average

**Final label distribution:**
- Low: ~57% | Medium: ~21% | High: ~22%

---

## Step 2: ML Model

### Features
- TF-IDF (unigrams + bigrams, 40k features) on `catalog_content`
- Scaled numeric `price` feature

### Model
- Logistic Regression (class-balanced, `max_iter=1000`)

### Performance (Validation — ~15k samples)
- **Macro F1 ≈ 0.82**
- Strong separation of Low and High quality classes
- Medium class shows expected ambiguity

---

## Step 3: Image Feature Experimentation (Abandoned)

ResNet-50 embeddings were tested as an additional signal.

| Images Used | Macro F1 | Observation |
|---|---|---|
| 1,000 | ~0.44 | Highly unstable |
| 10,000 | ~0.64 | Improved, still far below baseline |

**Decision:** Image features excluded — poor cost-to-benefit ratio vs text-only baseline. Documented as a validated negative result.

---

## Landing Page

A modern **SaaS-style landing page** (served at `/`) introduces the project with:

- Hero section with title and tagline
- **Why This Project** — weak supervision motivation
- **What Makes It Different** — rule-based label generation
- **Key Features** — Search, Filter, Analyze, Visualize
- **How It Works** — end-to-end flow diagram
- **Why It Matters** — company-side quality enforcement
- **Limitations** — honest constraints
- **Future Improvements** — roadmap
- **My Contribution** — proxy labeling system design
- CTA button linking directly to the Dashboard

**Design:** Dark mode, glassmorphism cards, animated glow orbs, scroll-triggered fade-in animations, fully responsive.

---

## Product Quality Dashboard

Served at `/dashboard`. An internal analytical tool for exploring quality predictions at scale.

### Features
- **Product Table** — Browse all 75,000 products with quality badges (Low / Medium / Good)
- **Intelligent Search** — Look up products by ID in real time
- **Smart Filtering** — Isolate products by quality tier
- **Detail Side Panel** — Clicking any product reveals:
  - Product metadata (ID, name, category, price)
  - Quality metrics (final score, text score, word count, price sanity, consistency)
  - ML reasoning summary
  - Mock review quality analysis
  - Product image (loaded from URL)
- **Data Visualization** — Natural language query interface:
  - Type any query, e.g. `"Show quality distribution as pie chart"`
  - Automatic chart type detection (bar or pie)
  - Supported: quality distribution, average price by quality, product counts
  - Real-time matplotlib chart rendered server-side → returned as base64 image
- **Dark / Light Mode Toggle** — Persisted via `localStorage`

### Tech Stack
- **Frontend:** Vanilla HTML, CSS, JavaScript
- **Backend:** FastAPI + pandas
- **Visualization:** Matplotlib + Seaborn (server-side rendering)
- **Data:** `train_with_quality_label.csv` (75,000 products)

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Landing page (HTML) |
| `GET` | `/dashboard` | Product Quality Dashboard (HTML) |
| `GET` | `/api/status` | API health + product count |
| `GET` | `/api/products` | List products (`search`, `quality`, `limit` params) |
| `GET` | `/api/products/{id}` | Full product detail with metrics & reviews |
| `GET` | `/api/visualize?query=...` | Generate chart from natural language query |
| `GET` | `/static/*` | Static files (CSS, JS) served from `frontend/` |

---

## How to Run

### 1. Generate the labeled dataset & train the model

```bash
# From the app/ directory
python backend/main.py
```

This reads `data/train.csv`, engineers weak labels, trains the model, and saves:
- `data/train_with_quality_label.csv`
- `models/model_logistic_regression.pkl`
- `models/tfidf_vectorizer.pkl`
- `models/price_scaler.pkl`

### 2. Start the API server

```bash
# From the app/ directory
python -m uvicorn backend.dashboard_api:app --host 0.0.0.0 --port 8000
```

Add `--reload` for development (auto-restarts on file changes):
```bash
python -m uvicorn backend.dashboard_api:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Open in browser

| URL | Page |
|---|---|
| `http://localhost:8000/` | Landing Page |
| `http://localhost:8000/dashboard` | Product Dashboard |
| `http://localhost:8000/api/status` | API Status JSON |
| `http://localhost:8000/docs` | FastAPI Swagger Docs |

---

## Docker

The project is fully containerized. The image runs the FastAPI server from the `/app` root so all relative paths (`../data/`, `../frontend/`) resolve correctly.

### Prerequisites
- Docker installed and running
- `data/train_with_quality_label.csv` must exist **before** building (generated by running `backend/main.py`)

### Build the image

```bash
# From the app/ directory
docker build -t ml-quality-app .
```

### Run the container

```bash
docker run -p 8000:8000 ml-quality-app
```

### Run with your local data mounted (recommended)

Since `data/train.csv` and `data/train_with_quality_label.csv` are excluded from the image (large files), mount the `data/` folder at runtime:

```bash
docker run -p 8000:8000 -v "$(pwd)/data:/app/data" ml-quality-app
```

> **Windows PowerShell:**
> ```powershell
> docker run -p 8000:8000 -v "${PWD}/data:/app/data" ml-quality-app
> ```

### Open in browser

Once started, visit:

| URL | Page |
|---|---|
| `http://localhost:8000/` | Landing Page |
| `http://localhost:8000/dashboard` | Product Dashboard |
| `http://localhost:8000/docs` | FastAPI Swagger Docs |

### What's excluded from the image (`.dockerignore`)

| Excluded | Reason |
|---|---|
| `__pycache__/`, `*.pyc` | Python bytecode cache |
| `notebooks/`, `*.ipynb` | Training notebooks not needed at serve time |
| `.git`, `.gitignore` | Version control metadata |
| `.env` | Secrets / environment config |

---

## Requirements

```
pandas==2.1.4
numpy==1.26.4
scikit-learn==1.3.2
scipy==1.11.4
joblib==1.3.2
matplotlib==3.8.1
seaborn
fastapi
uvicorn
```

Install with:
```bash
pip install -r requirements.txt
```

---

## Key Learnings

- Weak supervision produces strong, usable labels when grounded in data signals
- Rich textual descriptions dominate visual signals in catalog data
- Knowing **when to stop experimentation** is a critical ML engineering skill
- Negative results (image features) are valuable when properly validated
- Building an ML **system** — with serving, APIs, and UI — is fundamentally different from building a model

---

## Author

**Mayank A**  
B.Sc Computer Science  
Focused on Applied Machine Learning & Real-World ML Systems
