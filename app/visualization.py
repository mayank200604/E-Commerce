import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Setup
sns.set_style("whitegrid")
warnings.filterwarnings('ignore')

# Quality configuration
QUALITY_LABELS = {0: "Low Quality", 1: "Medium Quality", 2: "High Quality"}
QUALITY_COLORS = {0: "#FF6B6B", 1: "#FFD93D", 2: "#6BCF7F"}
QUALITY_WEIGHTS = {0: 0.3, 1: 0.6, 2: 1.0}


def load_data(file_path="train_with_quality_label.csv"):
    """Load and prepare the data"""
    try:
        df = pd.read_csv(file_path)
        
        # Add quality score if not present
        if "quality_score" not in df.columns:
            df["quality_score"] = df["quality_label"].map(QUALITY_WEIGHTS)
        
        return df
    
    except FileNotFoundError:
        return None


def parse_query(query, df):
    """
    Parse user query and extract what to visualize
    Returns: dict with filters, group_by, metric, chart_type
    """
    query_lower = query.lower()
    
    intent = {
        "filters": {},
        "group_by": None,
        "metric": "count",
        "chart_type": "bar",
        "title": query
    }
    
    # Detect chart type
    if "pie" in query_lower or "pie chart" in query_lower:
        intent["chart_type"] = "pie"
    else:
        intent["chart_type"] = "bar"
    
    # Detect what to group by
    if "quality" in query_lower or "qualities" in query_lower:
        intent["group_by"] = "quality_label"
    elif "price" in query_lower and ("range" in query_lower or "bin" in query_lower):
        intent["group_by"] = "price_bin"
    
    # Detect metric
    if "count" in query_lower or "number" in query_lower or "how many" in query_lower or "quantity" in query_lower:
        intent["metric"] = "count"
    elif "average price" in query_lower or "avg price" in query_lower or "mean price" in query_lower:
        intent["metric"] = "avg_price"
    elif "average score" in query_lower or "avg score" in query_lower:
        intent["metric"] = "avg_score"
    
    # Detect filters
    if "low quality" in query_lower or "low-quality" in query_lower:
        intent["filters"]["quality_label"] = 0
    elif "medium quality" in query_lower or "mid quality" in query_lower:
        intent["filters"]["quality_label"] = 1
    elif "high quality" in query_lower or "high-quality" in query_lower:
        intent["filters"]["quality_label"] = 2
    
    if "low price" in query_lower or "cheap" in query_lower:
        median = df['price'].median()
        intent["filters"]["price_filter"] = ("low", median)
    elif "high price" in query_lower or "expensive" in query_lower:
        median = df['price'].median()
        intent["filters"]["price_filter"] = ("high", median)
    
    return intent


def apply_filters(df, filters):
    """Apply filters to dataframe"""
    filtered_df = df.copy()
    
    for key, value in filters.items():
        if key == "quality_label":
            filtered_df = filtered_df[filtered_df["quality_label"] == value]
        elif key == "price_filter":
            filter_type, median = value
            if filter_type == "low":
                filtered_df = filtered_df[filtered_df["price"] < median]
            else:
                filtered_df = filtered_df[filtered_df["price"] >= median]
    
    return filtered_df


def calculate_metric(df, group_by, metric):
    """Calculate the metric based on grouping"""
    if metric == "count":
        result = df.groupby(group_by).size()
    elif metric == "avg_price":
        result = df.groupby(group_by)["price"].mean()
    elif metric == "avg_score":
        result = df.groupby(group_by)["quality_score"].mean()
    else:
        result = df.groupby(group_by).size()
    
    return result


def plot_chart(data, intent):
    """Generate bar or pie chart based on intent"""
    chart_type = intent["chart_type"]
    title = intent["title"]
    metric = intent["metric"]
    group_by = intent["group_by"]
    
    # Prepare labels and colors
    if group_by == "quality_label":
        labels = [QUALITY_LABELS[i] for i in data.index]
        colors = [QUALITY_COLORS[i] for i in data.index]
    else:
        labels = [str(x) for x in data.index]
        colors = plt.cm.Set3(range(len(data)))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if chart_type == "pie":
        # Pie chart
        ax.pie(data.values, labels=labels, colors=colors,
               autopct='%1.1f%%', startangle=90, 
               textprops={'fontsize': 11, 'weight': 'bold'})
        ax.set_title(title, fontsize=14, weight='bold', pad=20)
    
    else:
        # Bar chart
        bars = ax.bar(labels, data.values, color=colors, 
                     edgecolor='black', linewidth=1.5, alpha=0.8)
        
        # Labels
        metric_label = {
            "count": "Number of Products",
            "avg_price": "Average Price ($)",
            "avg_score": "Average Quality Score"
        }.get(metric, "Value")
        
        ax.set_ylabel(metric_label, fontsize=12, weight='bold')
        ax.set_xlabel('Category', fontsize=12, weight='bold')
        ax.set_title(title, fontsize=14, weight='bold', pad=20)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if metric == "count":
                label_text = f'{int(height):,}'
            else:
                label_text = f'{height:.2f}'
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   label_text, ha='center', va='bottom', 
                   fontsize=11, weight='bold')
        
        ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.show()


def visualize_from_query(query, df):
    """
    Main function: Parse query and generate appropriate chart
    """
    # Parse query
    intent = parse_query(query, df)
    
    # Apply filters
    filtered_df = apply_filters(df, intent["filters"])
    
    if len(filtered_df) == 0:
        return
    
    # Calculate metric
    result = calculate_metric(filtered_df, intent["group_by"], intent["metric"])
    
    # Generate chart
    plot_chart(result, intent)


def main():
    """Main execution"""
    
    # Load data
    df = load_data()
    if df is None:
        return
    
    # Demo: You can modify this query or make it interactive
    user_query = "Show average price by quality level"
    visualize_from_query(user_query, df)
    
    # Optional: Interactive mode
    # while True:
    #     user_query = input("\n🔍 Enter your query (or 'quit' to exit): ")
    #     if user_query.lower() in ['quit', 'exit', 'q']:
    #         break
    #     visualize_from_query(user_query, df)


if __name__ == "__main__":
    main()
