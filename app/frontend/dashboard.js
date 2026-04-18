// API Configuration
const API_BASE_URL = "http://localhost:8000";

// Data cache
let allProducts = [];
let productDetailsCache = {};

// Quality mapping
const qualityMap = {
    0: { label: "Low Quality", class: "quality-low" },
    1: { label: "Medium Risk", class: "quality-medium" },
    2: { label: "Good Quality", class: "quality-good" }
};

// State
let currentFilter = "all";
let currentSearch = "";
let filteredProducts = [];
let isLoading = false;

// DOM Elements
const tableBody = document.getElementById("tableBody");
const searchInput = document.getElementById("searchInput");
const filterButtons = document.querySelectorAll(".filter-btn");
const detailPanel = document.getElementById("detailPanel");
const overlay = document.getElementById("overlay");
const closePanel = document.getElementById("closePanel");
const panelContent = document.getElementById("panelContent");

// API Functions
async function fetchProducts(quality = null, search = null) {
    isLoading = true;
    renderLoadingState();

    try {
        let url = `${API_BASE_URL}/api/products?limit=500`;
        if (quality !== null && quality !== "all") {
            url += `&quality=${quality}`;
        }
        if (search) {
            url += `&search=${search}`;
        }

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        allProducts = data.products;
        filteredProducts = allProducts;
        isLoading = false;
        renderTable();
    } catch (error) {
        console.error("Error fetching products:", error);
        isLoading = false;
        renderErrorState(error.message);
    }
}

async function fetchProductDetail(productId) {
    // Check cache first
    if (productDetailsCache[productId]) {
        return productDetailsCache[productId];
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/products/${productId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        productDetailsCache[productId] = data;
        return data;
    } catch (error) {
        console.error("Error fetching product detail:", error);
        return null;
    }
}

// Initialize
function init() {
    initTheme();
    fetchProducts();
    attachEventListeners();
}

// Theme Management
function initTheme() {
    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");
    const themeText = document.getElementById("themeText");

    // Load saved theme or default to light
    const savedTheme = localStorage.getItem("dashboard-theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);
    updateThemeButton(savedTheme);

    // Toggle theme on button click
    themeToggle.addEventListener("click", () => {
        const currentTheme = document.documentElement.getAttribute("data-theme");
        const newTheme = currentTheme === "light" ? "dark" : "light";

        document.documentElement.setAttribute("data-theme", newTheme);
        localStorage.setItem("dashboard-theme", newTheme);
        updateThemeButton(newTheme);
    });

    function updateThemeButton(theme) {
        if (theme === "dark") {
            themeIcon.textContent = "☀️";
            themeText.textContent = "Light Mode";
        } else {
            themeIcon.textContent = "🌙";
            themeText.textContent = "Dark Mode";
        }
    }
}


// Render loading state
function renderLoadingState() {
    tableBody.innerHTML = `
        <tr>
            <td colspan="3" style="text-align: center; padding: 40px; color: #666;">
                Loading products...
            </td>
        </tr>
    `;
}

// Render error state
function renderErrorState(message) {
    tableBody.innerHTML = `
        <tr>
            <td colspan="3" style="text-align: center; padding: 40px; color: #c33;">
                Error loading products: ${message}<br>
                <small style="color: #666; margin-top: 8px; display: block;">
                    Make sure the API server is running on port 8000
                </small>
            </td>
        </tr>
    `;
}

// Render table
function renderTable() {
    tableBody.innerHTML = "";

    if (filteredProducts.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="3" style="text-align: center; padding: 40px; color: #999;">
                    No products found
                </td>
            </tr>
        `;
        return;
    }

    filteredProducts.forEach(product => {
        const row = document.createElement("tr");
        const qualityInfo = qualityMap[product.quality];

        row.innerHTML = `
            <td class="product-id">${product.id}</td>
            <td>${product.category}</td>
            <td><span class="quality-badge ${qualityInfo.class}">${qualityInfo.label}</span></td>
        `;

        row.addEventListener("click", () => openDetailPanel(product.id));
        tableBody.appendChild(row);
    });
}

// Open detail panel
async function openDetailPanel(productId) {
    // Show loading in panel
    panelContent.innerHTML = `
        <div style="text-align: center; padding: 40px; color: #666;">
            Loading product details...
        </div>
    `;
    detailPanel.classList.add("open");
    overlay.classList.add("active");

    // Fetch product details
    const product = await fetchProductDetail(productId);

    if (!product) {
        panelContent.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #c33;">
                Error loading product details
            </div>
        `;
        return;
    }

    const qualityInfo = qualityMap[product.quality];

    // Calculate review quality stats
    const goodReviews = product.reviews.filter(r => r.quality === "good").length;
    const poorReviews = product.reviews.filter(r => r.quality === "poor").length;

    panelContent.innerHTML = `
        <div class="detail-section">
            <h3>Product Information</h3>
            <div class="detail-row">
                <div class="detail-label">Product ID</div>
                <div class="detail-value">${product.id}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Product Name</div>
                <div class="detail-value">${product.product_name}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Category</div>
                <div class="detail-value">${product.category}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Price</div>
                <div class="detail-value">$${product.price.toFixed(2)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Overall Quality Result</div>
                <div class="detail-value">
                    <span class="quality-badge ${qualityInfo.class}">${qualityInfo.label}</span>
                </div>
            </div>
        </div>
        
        <div class="detail-section">
            <h3>Quality Metrics</h3>
            <div class="detail-row">
                <div class="detail-label">Final Score</div>
                <div class="detail-value">${product.metrics.final_score.toFixed(3)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Text Score</div>
                <div class="detail-value">${product.metrics.text_score.toFixed(3)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Word Count</div>
                <div class="detail-value">${product.metrics.word_count}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Price Sanity Score</div>
                <div class="detail-value">${product.metrics.price_sanity_score.toFixed(3)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Consistency Score</div>
                <div class="detail-value">${product.metrics.consistency_score.toFixed(3)}</div>
            </div>
            <div class="detail-row">
                <div class="detail-label">Price Outlier</div>
                <div class="detail-value">${product.metrics.price_outlier ? 'Yes' : 'No'}</div>
            </div>
        </div>
        
        <div class="detail-section">
            <h3>Quality Reason</h3>
            <div class="info-box">
                <p><strong>ML Model Analysis:</strong></p>
                <p style="margin-top: 8px;">
                    This product received a quality score of <strong>${product.metrics.final_score.toFixed(3)}</strong> based on:
                </p>
                <ul style="margin-top: 8px; margin-left: 20px; line-height: 1.8;">
                    <li>Content quality (text score: ${product.metrics.text_score.toFixed(3)})</li>
                    <li>Description completeness (${product.metrics.word_count} words)</li>
                    <li>Price reasonableness (sanity score: ${product.metrics.price_sanity_score.toFixed(3)})</li>
                    <li>Data consistency (score: ${product.metrics.consistency_score.toFixed(3)})</li>
                </ul>
            </div>
        </div>
        
        <div class="detail-section">
            <h3>Content Catalog & Review Quality Analysis</h3>
            <div class="info-box">
                <p><strong>Review Quality Summary:</strong> ${goodReviews} Good Reviews, ${poorReviews} Poor Reviews</p>
                <p style="margin-top: 8px;">Review content quality helps justify the product quality decision. High-quality reviews provide detailed, constructive feedback that aids in accurate product assessment.</p>
            </div>
            <div style="margin-top: 16px;">
                ${product.reviews.map((review, index) => `
                    <div class="review-item">
                        <div class="review-header">
                            <span style="font-size: 12px; color: #666; font-weight: 500;">Review ${index + 1}</span>
                            <span class="review-quality ${review.quality === 'good' ? 'review-good' : 'review-poor'}">
                                ${review.quality === 'good' ? 'Good Review' : 'Poor Review'}
                            </span>
                        </div>
                        <div class="review-text">${review.text}</div>
                    </div>
                `).join('')}
            </div>
        </div>
        
        ${product.image_link ? `
        <div class="detail-section">
            <h3>Product Image</h3>
            <img src="${product.image_link}" alt="${product.product_name}" 
                 style="max-width: 100%; border-radius: 8px; border: 1px solid #e0e0e0;"
                 onerror="this.style.display='none'">
        </div>
        ` : ''}
    `;
}

// Close detail panel
function closeDetailPanel() {
    detailPanel.classList.remove("open");
    overlay.classList.remove("active");
}

// Filter products
function filterProducts() {
    const quality = currentFilter === "all" ? null : parseInt(currentFilter);
    const search = currentSearch || null;
    fetchProducts(quality, search);
}

// Attach event listeners
function attachEventListeners() {
    // Search with debounce
    let searchTimeout;
    searchInput.addEventListener("input", (e) => {
        currentSearch = e.target.value;
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            filterProducts();
        }, 500); // Wait 500ms after user stops typing
    });

    // Filter buttons
    filterButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            filterButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentFilter = btn.dataset.filter;
            filterProducts();
        });
    });

    // Close panel
    closePanel.addEventListener("click", closeDetailPanel);
    overlay.addEventListener("click", closeDetailPanel);

    // Keyboard shortcut to close panel (Escape key)
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && detailPanel.classList.contains("open")) {
            closeDetailPanel();
        }
    });

    // Visualization modal listeners
    attachVisualizationListeners();
}

// Visualization Modal Functionality
function attachVisualizationListeners() {
    const tryVizBtn = document.getElementById("tryVizBtn");
    const vizModal = document.getElementById("vizModal");
    const closeVizModal = document.getElementById("closeVizModal");
    const vizSubmitBtn = document.getElementById("vizSubmitBtn");
    const vizQuery = document.getElementById("vizQuery");
    const exampleBtns = document.querySelectorAll(".example-query-btn");

    // Open modal
    tryVizBtn.addEventListener("click", () => {
        vizModal.classList.add("active");
        overlay.classList.add("active");
        vizQuery.focus();
    });

    // Close modal
    closeVizModal.addEventListener("click", () => {
        closeVizModalFunc(vizModal);
    });

    // Close on overlay click (only if clicking on viz modal)
    overlay.addEventListener("click", (e) => {
        if (vizModal.classList.contains("active")) {
            closeVizModalFunc(vizModal);
        }
    });

    // Submit visualization
    vizSubmitBtn.addEventListener("click", () => {
        const query = vizQuery.value.trim();
        if (query) {
            generateVisualization(query);
        }
    });

    // Submit on Enter key
    vizQuery.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            const query = vizQuery.value.trim();
            if (query) {
                generateVisualization(query);
            }
        }
    });

    // Example query buttons
    exampleBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const query = btn.dataset.query;
            vizQuery.value = query;
            generateVisualization(query);
        });
    });

    // Keyboard shortcut to close viz modal (Escape key)
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && vizModal.classList.contains("active")) {
            closeVizModalFunc(vizModal);
        }
    });
}

function closeVizModalFunc(modal) {
    const vizModal = modal || document.getElementById("vizModal");
    vizModal.classList.remove("active");

    // Clear/reset the modal content
    const vizQuery = document.getElementById("vizQuery");
    const vizLoading = document.getElementById("vizLoading");
    const vizError = document.getElementById("vizError");
    const vizChart = document.getElementById("vizChart");

    vizQuery.value = "";  // Clear input
    vizLoading.style.display = "none";  // Hide loading
    vizError.style.display = "none";  // Hide error
    vizChart.innerHTML = "";  // Clear chart

    // Only close overlay if detail panel is also closed
    if (!detailPanel.classList.contains("open")) {
        overlay.classList.remove("active");
    }
}

async function generateVisualization(query) {
    const vizLoading = document.getElementById("vizLoading");
    const vizError = document.getElementById("vizError");
    const vizChart = document.getElementById("vizChart");

    // Show loading
    vizLoading.style.display = "block";
    vizError.style.display = "none";
    vizChart.innerHTML = "";

    try {
        const response = await fetch(`${API_BASE_URL}/api/visualize?query=${encodeURIComponent(query)}`);
        const data = await response.json();

        // Hide loading
        vizLoading.style.display = "none";

        if (data.error) {
            // Show error
            vizError.textContent = data.error;
            vizError.style.display = "block";
        } else if (data.success) {
            // Show chart
            vizChart.innerHTML = `<img src="${data.image}" alt="${data.query}" />`;
        }
    } catch (error) {
        console.error("Error generating visualization:", error);
        vizLoading.style.display = "none";
        vizError.textContent = `Error: ${error.message}`;
        vizError.style.display = "block";
    }
}

// Initialize on load
document.addEventListener("DOMContentLoaded", init);
