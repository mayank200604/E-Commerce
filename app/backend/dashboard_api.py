from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import pandas as pd
import re
from typing import Optional
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

# ── Path resolution ───────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR     = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
DATA_FILE    = os.path.join(DATA_DIR, "train_with_quality_label.csv")

app = FastAPI(title="Product Quality Dashboard API")

# ── Lazy data loader ──────────────────────────────────────────────────────────
# `_df` is intentionally None at startup so Render's health-check instant.
# Data is loaded once on the first real endpoint call and reused thereafter.
_df = None

def get_data() -> pd.DataFrame:
    """Return the cached DataFrame, loading it from disk on first call."""
    global _df
    if _df is None:
        if not os.path.exists(DATA_FILE):
            raise FileNotFoundError(
                f"Data file not found at {DATA_FILE}. "
                "Run backend/main.py first to generate the dataset."
            )
        print("Loading product data (first request)...")
        _df = pd.read_csv(DATA_FILE)
        print(f"Loaded {len(_df)} products")
    return _df


# ── Helper functions ──────────────────────────────────────────────────────────

def extract_product_name(catalog_content):
    """Extract product name from catalog content."""
    match = re.search(r'Item Name:\s*(.+?)(?:\n|$)', catalog_content)
    if match:
        return match.group(1).strip()
    return "Unknown Product"

def extract_category(catalog_content):
    """Extract or infer category from product name."""
    name = extract_product_name(catalog_content).lower()
    if any(w in name for w in ['phone', 'laptop', 'tablet', 'headphone', 'camera', 'tv', 'electronics']):
        return "Electronics"
    elif any(w in name for w in ['shirt', 'pants', 'dress', 'shoes', 'clothing', 'jacket']):
        return "Clothing"
    elif any(w in name for w in ['kitchen', 'home', 'furniture', 'decor', 'bedding']):
        return "Home & Kitchen"
    elif any(w in name for w in ['book', 'novel', 'guide', 'manual']):
        return "Books"
    elif any(w in name for w in ['toy', 'game', 'puzzle', 'doll']):
        return "Toys & Games"
    elif any(w in name for w in ['beauty', 'cosmetic', 'skincare', 'makeup', 'shampoo']):
        return "Beauty & Personal Care"
    elif any(w in name for w in ['sports', 'fitness', 'outdoor', 'camping', 'bike']):
        return "Sports & Outdoors"
    elif any(w in name for w in ['food', 'snack', 'sauce', 'beverage', 'grocery']):
        return "Food & Grocery"
    else:
        return "Other"

def generate_mock_reviews(quality_label, catalog_content):
    """Generate mock reviews based on quality label."""
    product_name = extract_product_name(catalog_content)
    if quality_label == 2:
        return [
            {"text": f"Excellent {product_name}! Works perfectly as described. Very satisfied with the purchase.", "quality": "good"},
            {"text": "Great value for money. Highly recommend this to anyone looking for quality.", "quality": "good"},
            {"text": "Fast shipping and product matches description perfectly.", "quality": "good"}
        ]
    elif quality_label == 1:
        return [
            {"text": f"The {product_name} is okay but could be better. Average quality.", "quality": "poor"},
            {"text": "Works as expected but nothing special.", "quality": "good"},
            {"text": "Decent for the price, but has some minor issues.", "quality": "poor"}
        ]
    else:
        return [
            {"text": f"Poor quality {product_name}, not as shown in pictures.", "quality": "poor"},
            {"text": "Disappointed with this purchase. Would not recommend.", "quality": "poor"},
            {"text": "Not worth the money. Very unhappy with quality.", "quality": "poor"}
        ]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def health_check():
    """Lightweight health check — returns instantly, no data loading."""
    return {
        "status": "ok",
        "service": "Product Quality Dashboard API",
        "endpoints": {
            "landing":        "/landing",
            "dashboard":      "/dashboard",
            "products":       "/api/products",
            "product_detail": "/api/products/{product_id}",
            "visualize":      "/api/visualize",
            "status":         "/api/status"
        }
    }

@app.get("/landing")
def serve_landing():
    """Serve the project landing page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "landing.html"))

@app.get("/api/status")
def api_status():
    """API status with dataset info — triggers data load on first call."""
    try:
        df = get_data()
        return {
            "status": "Dashboard API is running",
            "total_products": len(df),
            "data_loaded": True,
            "endpoints": {
                "products":       "/api/products",
                "product_detail": "/api/products/{product_id}",
                "dashboard":      "/dashboard"
            }
        }
    except FileNotFoundError as e:
        return JSONResponse(status_code=503, content={"status": "error", "detail": str(e)})

@app.get("/api/products")
def get_products(
    search:  Optional[str] = None,
    quality: Optional[int] = Query(None, ge=0, le=2),
    limit:   int = Query(500, le=1000)
):
    """Get list of products with optional filtering."""
    try:
        df = get_data()
    except FileNotFoundError as e:
        return JSONResponse(status_code=503, content={"error": str(e), "total": 0, "products": []})

    filtered_df = df.copy()

    if quality is not None:
        filtered_df = filtered_df[filtered_df['quality_label'] == quality]

    if search:
        filtered_df = filtered_df[
            filtered_df['sample_id'].astype(str).str.contains(search, case=False)
        ]

    filtered_df = filtered_df.head(limit)

    products = []
    for _, row in filtered_df.iterrows():
        products.append({
            "id":           f"PROD-{row['sample_id']}",
            "sample_id":    int(row['sample_id']),
            "category":     extract_category(row['catalog_content']),
            "quality":      int(row['quality_label']),
            "product_name": extract_product_name(row['catalog_content']),
            "price":        float(row['price']),
            "final_score":  float(row['final_score'])
        })

    return {"total": len(products), "products": products}

@app.get("/api/products/{product_id}")
def get_product_detail(product_id: str):
    """Get detailed information for a specific product."""
    try:
        df = get_data()
    except FileNotFoundError as e:
        return JSONResponse(status_code=503, content={"error": str(e)})

    sample_id = int(product_id.replace("PROD-", ""))
    product_row = df[df['sample_id'] == sample_id]

    if len(product_row) == 0:
        return JSONResponse(status_code=404, content={"error": "Product not found"})

    row = product_row.iloc[0]
    reviews = generate_mock_reviews(int(row['quality_label']), row['catalog_content'])

    return {
        "id":             f"PROD-{row['sample_id']}",
        "sample_id":      int(row['sample_id']),
        "product_name":   extract_product_name(row['catalog_content']),
        "category":       extract_category(row['catalog_content']),
        "quality":        int(row['quality_label']),
        "price":          float(row['price']),
        "image_link":     row['image_link'],
        "catalog_content": row['catalog_content'],
        "metrics": {
            "word_count":         int(row['word_count']),
            "text_score":         float(row['text_score']),
            "price_outlier":      bool(row['price_outlier']),
            "price_sanity_score": float(row['price_sanity_score']),
            "consistency_score":  float(row['consistency_score']),
            "final_score":        float(row['final_score'])
        },
        "reviews": reviews
    }

@app.get("/dashboard")
def serve_dashboard():
    """Serve the dashboard HTML page."""
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))

@app.get("/api/visualize")
def generate_visualization(query: str = Query(..., description="Natural language query for visualization")):
    """Generate visualization chart from natural language query."""
    try:
        df = get_data()
    except FileNotFoundError as e:
        return {"error": str(e)}

    QUALITY_LABELS = {0: "Low Quality", 1: "Medium Quality", 2: "High Quality"}
    QUALITY_COLORS = {0: "#FF6B6B",     1: "#FFD93D",        2: "#6BCF7F"}

    sns.set_style("whitegrid")

    try:
        query_lower = query.lower()
        chart_type  = "pie" if "pie" in query_lower else "bar"

        if "quality" in query_lower:
            result = df['quality_label'].value_counts().sort_index()
            labels = [QUALITY_LABELS[i] for i in result.index]
            colors = [QUALITY_COLORS[i]  for i in result.index]
            title  = query

            fig, ax = plt.subplots(figsize=(10, 6))
            if chart_type == "pie":
                ax.pie(result.values, labels=labels, colors=colors,
                       autopct='%1.1f%%', startangle=90,
                       textprops={'fontsize': 11, 'weight': 'bold'})
                ax.set_title(title, fontsize=14, weight='bold', pad=20)
            else:
                bars = ax.bar(labels, result.values, color=colors,
                              edgecolor='black', linewidth=1.5, alpha=0.8)
                ax.set_ylabel('Number of Products', fontsize=12, weight='bold')
                ax.set_xlabel('Quality Level',       fontsize=12, weight='bold')
                ax.set_title(title,                  fontsize=14, weight='bold', pad=20)
                for bar in bars:
                    h = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2., h,
                            f'{int(h):,}', ha='center', va='bottom',
                            fontsize=11, weight='bold')
                ax.grid(axis='y', alpha=0.3)

        elif "price" in query_lower:
            result = df.groupby('quality_label')['price'].mean().sort_index()
            labels = [QUALITY_LABELS[i] for i in result.index]
            colors = [QUALITY_COLORS[i]  for i in result.index]
            title  = query

            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(labels, result.values, color=colors,
                          edgecolor='black', linewidth=1.5, alpha=0.8)
            ax.set_ylabel('Average Price ($)', fontsize=12, weight='bold')
            ax.set_xlabel('Quality Level',     fontsize=12, weight='bold')
            ax.set_title(title,                fontsize=14, weight='bold', pad=20)
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., h,
                        f'${h:.2f}', ha='center', va='bottom',
                        fontsize=11, weight='bold')
            ax.grid(axis='y', alpha=0.3)

        else:
            return {
                "error": (
                    "This visualization is not available.\n\n"
                    "Available Data for Visualization:\n"
                    "• Quality labels (Low/Medium/High)\n"
                    "• Price\n"
                    "• Product counts\n\n"
                    "Supported Chart Types:\n"
                    "• Bar charts\n"
                    "• Pie charts\n\n"
                    "Please search for charts using only these available data types."
                )
            }

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)

        return {"success": True, "image": f"data:image/png;base64,{img_base64}", "query": query}

    except Exception as e:
        return {"error": str(e)}


# ── Static files (CSS / JS) — must be registered AFTER all routes ─────────────
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
