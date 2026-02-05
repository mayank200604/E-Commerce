from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
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

app = FastAPI(title="Product Quality Dashboard API")

# No CORS needed since frontend is served from the same origin (localhost:8000)

# Load data once at startup
print("Loading product data...")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "train_with_quality_label.csv"))

def extract_product_name(catalog_content):
    """Extract product name from catalog content"""
    match = re.search(r'Item Name:\s*(.+?)(?:\n|$)', catalog_content)
    if match:
        return match.group(1).strip()
    return "Unknown Product"

def extract_category(catalog_content):
    """Extract or infer category from product name"""
    name = extract_product_name(catalog_content).lower()
    
    # Simple category mapping based on keywords
    if any(word in name for word in ['phone', 'laptop', 'tablet', 'headphone', 'camera', 'tv', 'electronics']):
        return "Electronics"
    elif any(word in name for word in ['shirt', 'pants', 'dress', 'shoes', 'clothing', 'jacket']):
        return "Clothing"
    elif any(word in name for word in ['kitchen', 'home', 'furniture', 'decor', 'bedding']):
        return "Home & Kitchen"
    elif any(word in name for word in ['book', 'novel', 'guide', 'manual']):
        return "Books"
    elif any(word in name for word in ['toy', 'game', 'puzzle', 'doll']):
        return "Toys & Games"
    elif any(word in name for word in ['beauty', 'cosmetic', 'skincare', 'makeup', 'shampoo']):
        return "Beauty & Personal Care"
    elif any(word in name for word in ['sports', 'fitness', 'outdoor', 'camping', 'bike']):
        return "Sports & Outdoors"
    elif any(word in name for word in ['food', 'snack', 'sauce', 'beverage', 'grocery']):
        return "Food & Grocery"
    else:
        return "Other"

def generate_mock_reviews(quality_label, catalog_content):
    """Generate mock reviews based on quality label"""
    product_name = extract_product_name(catalog_content)
    
    if quality_label == 2:  # Good Quality
        return [
            {"text": f"Excellent {product_name}! Works perfectly as described. Very satisfied with the purchase.", "quality": "good"},
            {"text": "Great value for money. Highly recommend this to anyone looking for quality.", "quality": "good"},
            {"text": "Fast shipping and product matches description perfectly.", "quality": "good"}
        ]
    elif quality_label == 1:  # Medium Risk
        return [
            {"text": f"The {product_name} is okay but could be better. Average quality.", "quality": "poor"},
            {"text": "Works as expected but nothing special.", "quality": "good"},
            {"text": "Decent for the price, but has some minor issues.", "quality": "poor"}
        ]
    else:  # Low Quality
        return [
            {"text": f"Poor quality {product_name}, not as shown in pictures.", "quality": "poor"},
            {"text": "Disappointed with this purchase. Would not recommend.", "quality": "poor"},
            {"text": "Not worth the money. Very unhappy with quality.", "quality": "poor"}
        ]

@app.get("/")
def root():
    return {
        "status": "Dashboard API is running",
        "total_products": len(df),
        "endpoints": {
            "products": "/api/products",
            "product_detail": "/api/products/{product_id}",
            "dashboard": "/dashboard"
        }
    }

@app.get("/api/products")
def get_products(
    search: Optional[str] = None,
    quality: Optional[int] = Query(None, ge=0, le=2),
    limit: int = Query(500, le=1000)
):
    """Get list of products with optional filtering"""
    filtered_df = df.copy()
    
    # Filter by quality
    if quality is not None:
        filtered_df = filtered_df[filtered_df['quality_label'] == quality]
    
    # Filter by search (product ID)
    if search:
        filtered_df = filtered_df[
            filtered_df['sample_id'].astype(str).str.contains(search, case=False)
        ]
    
    # Limit results
    filtered_df = filtered_df.head(limit)
    
    # Format response
    products = []
    for _, row in filtered_df.iterrows():
        products.append({
            "id": f"PROD-{row['sample_id']}",
            "sample_id": int(row['sample_id']),
            "category": extract_category(row['catalog_content']),
            "quality": int(row['quality_label']),
            "product_name": extract_product_name(row['catalog_content']),
            "price": float(row['price']),
            "final_score": float(row['final_score'])
        })
    
    return {
        "total": len(products),
        "products": products
    }

@app.get("/api/products/{product_id}")
def get_product_detail(product_id: str):
    """Get detailed information for a specific product"""
    # Extract sample_id from product_id (format: PROD-12345)
    sample_id = int(product_id.replace("PROD-", ""))
    
    # Find product
    product_row = df[df['sample_id'] == sample_id]
    
    if len(product_row) == 0:
        return {"error": "Product not found"}
    
    row = product_row.iloc[0]
    
    # Generate mock reviews based on quality
    reviews = generate_mock_reviews(int(row['quality_label']), row['catalog_content'])
    
    return {
        "id": f"PROD-{row['sample_id']}",
        "sample_id": int(row['sample_id']),
        "product_name": extract_product_name(row['catalog_content']),
        "category": extract_category(row['catalog_content']),
        "quality": int(row['quality_label']),
        "price": float(row['price']),
        "image_link": row['image_link'],
        "catalog_content": row['catalog_content'],
        "metrics": {
            "word_count": int(row['word_count']),
            "text_score": float(row['text_score']),
            "price_outlier": bool(row['price_outlier']),
            "price_sanity_score": float(row['price_sanity_score']),
            "consistency_score": float(row['consistency_score']),
            "final_score": float(row['final_score'])
        },
        "reviews": reviews
    }

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/dashboard")
def serve_dashboard():
    return FileResponse(os.path.join(BASE_DIR, "dashboard.html"))

@app.get("/api/visualize")
def generate_visualization(query: str = Query(..., description="Natural language query for visualization")):
    """Generate visualization chart from natural language query"""
    
    # Configuration
    QUALITY_LABELS = {0: "Low Quality", 1: "Medium Quality", 2: "High Quality"}
    QUALITY_COLORS = {0: "#FF6B6B", 1: "#FFD93D", 2: "#6BCF7F"}
    
    sns.set_style("whitegrid")
    
    try:
        query_lower = query.lower()
        
        # Parse query
        chart_type = "pie" if "pie" in query_lower else "bar"
        
        # Determine what to visualize
        if "quality" in query_lower:
            # Calculate quality distribution
            result = df['quality_label'].value_counts().sort_index()
            labels = [QUALITY_LABELS[i] for i in result.index]
            colors = [QUALITY_COLORS[i] for i in result.index]
            title = query
            
            # Create figure
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
                ax.set_xlabel('Quality Level', fontsize=12, weight='bold')
                ax.set_title(title, fontsize=14, weight='bold', pad=20)
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height):,}', ha='center', va='bottom',
                           fontsize=11, weight='bold')
                ax.grid(axis='y', alpha=0.3)
            
        elif "price" in query_lower:
            # Average price by quality
            result = df.groupby('quality_label')['price'].mean().sort_index()
            labels = [QUALITY_LABELS[i] for i in result.index]
            colors = [QUALITY_COLORS[i] for i in result.index]
            title = query
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(labels, result.values, color=colors,
                         edgecolor='black', linewidth=1.5, alpha=0.8)
            ax.set_ylabel('Average Price ($)', fontsize=12, weight='bold')
            ax.set_xlabel('Quality Level', fontsize=12, weight='bold')
            ax.set_title(title, fontsize=14, weight='bold', pad=20)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'${height:.2f}', ha='center', va='bottom',
                       fontsize=11, weight='bold')
            ax.grid(axis='y', alpha=0.3)
        
        else:
            return {
                "error": "This visualization is not available.\n\n"
                        "Available Data for Visualization:\n"
                        "• Quality labels (Low/Medium/High)\n"
                        "• Price\n"
                        "• Product counts\n\n"
                        "Supported Chart Types:\n"
                        "• Bar charts\n"
                        "• Pie charts\n\n"
                        "Please search for charts using only these available data types."
            }
        
        # Convert plot to base64 image
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return {
            "success": True,
            "image": f"data:image/png;base64,{img_base64}",
            "query": query
        }
        
    except Exception as e:
        return {"error": str(e)}

# Mount static files to serve CSS and JS
# Must be done AFTER all routes to avoid conflicts
app.mount(
    "/static",
    StaticFiles(directory=os.path.dirname(os.path.abspath(__file__))),
    name="static"
)

