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
├── train_with_quality_label.csv
│ └── Generated dataset with engineered labels
│
├── train.csv / test.csv
│ └── Raw data (not included due to size)


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

## Key Learnings

- Weak supervision can produce strong, usable labels when grounded in data.
- Rich textual descriptions often dominate visual signals in catalog data.
- Knowing **when to stop experimentation** is a critical ML skill.
- Negative results are valuable when properly validated and documented.

---

## Requirements

- Python 3.8+
- pandas, numpy, scikit-learn, scipy
- lightgbm (optional)
- torch, torchvision (for image experiments)

---

## How to Run

1. Run `main.ipynb`  
   → Performs EDA and generates `train_with_quality_label.csv`

2. Run `train.ipynb`  
   → Trains and evaluates the final model

---

## Author

**Mayank A**  
B.Sc Computer Science  
Focused on Applied Machine Learning & Real-World ML
