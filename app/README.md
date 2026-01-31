# E-Commerce Product Quality Classification (Weakly Supervised ML)

## Overview

This project builds an **end-to-end machine learning pipeline** to assess the **quality of e-commerce product catalog entries** when **no ground-truth labels are available**.

Instead of relying on predefined labels, the project uses **weak supervision** to engineer a proxy `quality_label` from observable signals such as:
- richness of product descriptions,
- price sanity and outliers,
- consistency between price and textual detail.

The final system demonstrates how real-world ML problems are framed, validated, and **intentionally constrained** based on empirical evidence.

---

## Problem Statement

> **How can we automatically assess the quality of product listings when explicit quality labels do not exist?**

This mirrors real production settings where:
- labels are unavailable or expensive,
- quality must be inferred from indirect signals,
- decisions must be justified with data rather than assumptions.

---

## Dataset Description

**Training data (~75,000 rows)** contains:
- `catalogue_content` — product description text  
- `price` — product price  
- `image_url` — URL to product image  

A separate test file exists but is **not used for model development** due to missing price information and lack of labels.

---

## Project Structure

├── main.ipynb
│ └── Exploratory analysis & weak label engineering
│
├── train.ipynb
│ └── Feature extraction, modeling, and evaluation
│
├── main.py
│ └── Production ML pipeline script
│
├── api.py
│ └── Original FastAPI endpoint
│
├── dashboard_api.py
│ └── Dashboard backend API (serves real product data)
│
├── dashboard.html / dashboard.css / dashboard.js
│ └── Product Quality Analysis Dashboard (frontend)
│
├── visualization.py
│ └── Standalone visualization script for query-based chart generation
│
├── train_with_quality_label.csv
│ └── Generated dataset with engineered labels
│
├── train.csv / test.csv
│ └── Raw data (not included due to size)
│
├── *.pkl files
│ └── Trained model artifacts (TF-IDF vectorizer, scaler, model)


---

## Step 1: Exploratory Signal Analysis

Before modeling, extensive analysis was performed to understand signal quality:

- Text descriptions are **rich and technical**
  - Mean length ≈ 148 words
  - >99% contain numbers and units
- Price distribution is skewed but meaningful
  - ~7% price outliers detected
- Strong empirical relationship observed:
  - higher price → richer descriptions

This analysis justified using **text and price** as the primary signals.

---

## Step 2: Weak Label Engineering

Since no labels were provided, a **3-class quality label** was engineered:

- `0` → Low quality / risky  
- `1` → Medium quality  
- `2` → High quality  

### Label construction used:
1. **Text quality score** (word-count percentiles)
2. **Price sanity score** (IQR-based outlier detection)
3. **Price–text consistency score**

These signals were combined into a composite score and discretized into classes.

**Final label distribution:**
- Low: ~57%
- Medium: ~21%
- High: ~22%

This distribution is realistic and learnable.

---

## Step 3: Baseline Model (Final Model)

### Features
- TF-IDF (unigrams + bigrams) on product descriptions  
- Scaled numeric price feature  

### Model
- Logistic Regression (class-balanced)

### Performance (Validation set ≈ 15,000 samples)

- **Macro F1 ≈ 0.82**
- Strong separation of low and high quality classes
- Medium class shows expected ambiguity

This model is **stable, interpretable, and production-viable**.

---

## Step 4: Image Feature Experimentation (Intentionally Abandoned)

To evaluate whether images add value, pretrained **ResNet-50 embeddings** were tested.

### Experiments

| Images Used | Macro F1 | Observation |
|------------|----------|-------------|
| 1,000      | ~0.44    | Highly unstable |
| 10,000     | ~0.64    | Improved, but still far below baseline |

### Conclusion

- Image embeddings contain **weak discriminative signal**
- Scaling images improves results marginally
- Performance **saturates well below the text-only baseline**

> **Decision:** Image features were excluded from the final model due to poor cost-to-benefit ratio.

This decision was made **based on evidence**, not assumption.

---

## Final Model Choice

✔ **Text (TF-IDF) + Price**  
✔ Logistic Regression  
✔ **Macro F1 ≈ 0.82**  

Image features are documented as an explored but rejected modality.

---

## Product Quality Dashboard

A clean, minimal internal dashboard has been built to visualize and analyze product quality predictions.

### Features
- **Product Table**: Browse all products with quality status (Low/Medium/Good)
- **Search & Filter**: Find products by ID or filter by quality level
- **Detail Panel**: View comprehensive product information including:
  - Product metadata (ID, name, category, price)
  - Quality metrics (final score, text score, consistency score, etc.)
  - ML model reasoning and feature importance
  - Review quality analysis
  - Product images
- **📊 Data Visualization** (NEW): Interactive query-based chart generation
  - Natural language query interface
  - Automatic chart type selection (bar or pie)
  - Supported visualizations:
    - Quality distribution across products
    - Average price by quality level
    - Product counts by quality category
  - Real-time chart generation with matplotlib
  - Modal popup interface for clean UX

### Tech Stack
- **Frontend**: Vanilla HTML, CSS, JavaScript (no frameworks)
- **Backend**: FastAPI with pandas for data processing
- **Visualization**: Matplotlib (server-side rendering), Seaborn
- **Data Source**: `train_with_quality_label.csv` (75,000 products)

### Dashboard Design Principles
- Flat, readable, professional layout
- Developer-focused (not flashy)
- No animations or complex nested pages
- Clean typography and color-coded quality badges
- Query-based visualization with automatic chart selection

---

## Key Learnings

- Weak supervision can produce strong, usable labels when grounded in data.
- Rich textual descriptions often dominate visual signals in catalog data.
- Knowing **when to stop experimentation** is a critical ML skill.
- Negative results are valuable when properly validated and documented.

---

## Requirements

```
pandas
numpy
scikit-learn
scipy
matplotlib
seaborn
lightgbm (optional)
torch
torchvision (for image experiments)
fastapi
uvicorn
```

Install with:
```bash
pip install -r requirements.txt
```

---

## How to Run

### Option 1: Run ML Pipeline Only

1. Run `main.ipynb`  
   → Performs EDA and generates `train_with_quality_label.csv`

2. Run `train.ipynb`  
   → Trains and evaluates the final model

3. Or run the production script:
   ```bash
   python main.py
   ```

### Option 2: Run Dashboard (Recommended)

1. **Start the Dashboard API** (in one terminal):
   ```bash
   python dashboard_api.py
   ```
   This will start the backend API on `http://localhost:8000`

2. **Start the HTTP Server** (in another terminal):
   ```bash
   python -m http.server 8080
   ```

3. **Open the Dashboard**:
   Navigate to `http://localhost:8000/dashboard` in your browser

4. **Explore Products**:
   - Browse products from the database
   - Search by Product ID
   - Filter by quality level (Low/Medium/Good)
   - Click any product to see detailed analysis

5. **Try Visualization** (NEW):
   - Click the "Try Visualization" button in the filters section
   - Enter a natural language query like:
     - "Show quality distribution as pie chart"
     - "Show the quantity of products for each quality type"
     - "Show average price by quality level"
   - Or click one of the example queries
   - Charts are generated in real-time and displayed in a modal popup
   - Close the modal to reset and try another query

### API Endpoints

- `GET /` - API status
- `GET /api/products` - List products (with optional filters)
  - Query params: `search`, `quality`, `limit`
- `GET /api/products/{product_id}` - Get product details
- `GET /api/visualize` - Generate visualization chart from query (NEW)
  - Query param: `query` (natural language query string)
  - Returns: Base64-encoded PNG image
- `GET /dashboard` - Serve dashboard HTML

---

## Author

**Mayank A**  
B.Sc Computer Science  
Focused on Applied Machine Learning & Real-World ML

