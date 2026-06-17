# 📦 Supply Chain Analytics — Moving from Complexity to Clarity

A complete end-to-end supply chain analytics project for **Just In Time**, a global e-commerce company.  
This project identifies shipment delays, inventory imbalances, and profit inefficiencies — and proposes data-driven solutions through interactive Tableau dashboards.

**🔗 Tableau Story Dashboard:** [View Live](https://public.tableau.com/app/profile/subhrajit.majumder6368/viz/supplychainoperationsandanalyticssuite/BusinessPerformanceDashboard_)
                        
**🔗 Live Webapp link:** https://supply-chain-analytics-hhxowpozpj5upksmubvakv.streamlit.app/

---

## 🛠️ Tools & Technologies

| Tool | Purpose |
|---|---|
| Python (Pandas, NumPy) | Data cleaning, preprocessing, feature engineering |
| Matplotlib & Seaborn | Exploratory data analysis (EDA) visualizations |
| Tableau Public | Interactive dashboards & story |
| Jupyter Notebook | Development & documentation environment |

---

## 📁 Project Structure

```
Supply-Chain-Analytics/
│
├── Datasets/
│   ├── orders_and_shipment.csv          # Raw orders & shipment data
│   ├── inventory.csv                    # Raw warehouse inventory data
│   └── fulfillment.csv                  # Raw order fulfillment days
│
├── plots/                               # Auto-generated EDA charts
│   ├── monthly_profit_trend.png
│   ├── delay_by_shipment_mode.png
│   ├── profit_by_market.png
│   ├── top10_products_profit.png
│   ├── abc_segmentation.png
│   ├── processing_time_dist.png
│   ├── storage_cost_top10.png
│   └── correlation_heatmap.png
│
├── Supply_Chain_Analytics.ipynb         # Main analysis notebook
├── dashboard.png                        # Tableau dashboard screenshot
├── JIT_Logo.PNG                         # Company logo
├── requirements.txt                     # Python dependencies
└── README.md
```

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/subhrajit67/Supply-Chain-Analytics.git
cd Supply-Chain-Analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the notebook
jupyter notebook Supply_Chain_Analytics.ipynb
```

> All cells run top-to-bottom. Cleaned CSVs and EDA plots are exported automatically.

---

## 🎯 Objective

As the data analyst for Just In Time, the goal is to:
- Identify **supply chain inefficiencies** in shipment and inventory
- Perform **EDA** to uncover patterns in profit, delays, and inventory
- Build **5 interactive Tableau dashboards** covering business performance, inventory, and shipment analysis
- Propose **actionable business improvements** backed by data

---

## 📊 Dataset Overview

Three datasets covering the period **2015–2017**:

| Dataset | Rows | Description |
|---|---|---|
| `orders_and_shipment.csv` | 30,871 | Order details, customer info, shipment mode, profit, discount |
| `inventory.csv` | 4,200 | Monthly warehouse inventory per product, storage cost per unit |
| `fulfillment.csv` | 118 | Average fulfillment days per product |

---

## 🔧 Data Preprocessing & Feature Engineering

Steps performed in the notebook:

1. **Data Quality Check** — null values, duplicates, and statistical summary
2. **Column Cleaning** — stripped whitespace from all column headers
3. **Discount Fix** — replaced `'-'` string values with `0` in `Discount %`
4. **Country Fix** — resolved encoding artefacts (`\xa0`, `\x92`, etc.) in country names
5. **Date Engineering** — merged year/month/day columns → `Order Datetime`, `Shipment Datetime`
6. **Order Processing Time** — `Shipment Datetime − Order Datetime` (same-day negatives → 0)
7. **Shipment Delay** — `Actual days − Scheduled days` + binary `Is Delay` flag
8. **Storage Cost** — `Warehouse Inventory × Inventory Cost Per Unit`
9. **ABC Segmentation** — classified products into A/B/C tiers by cumulative profit contribution (A ≤ 70%, B ≤ 90%, C = rest)
10. **Export** — 3 clean CSVs exported for Tableau

---

## 📈 Exploratory Data Analysis (EDA)

The notebook generates **8 visualizations** that answer key business questions:

| Chart | Business Question |
|---|---|
| Monthly Profit Trend | When was performance best/worst? |
| Delay Rate by Shipment Mode | Which shipping methods are most delayed? |
| Profit by Customer Market | Which regions drive the most revenue? |
| Top 10 Products by Profit | Where is profit concentrated? |
| ABC Segmentation Donuts | How many products drive how much profit? |
| Processing Time Distribution | What does a typical order cycle look like? |
| Top 10 Storage Cost Products | Which products cost most to hold? |
| Correlation Heatmap | How do numeric variables relate to each other? |

---

## 📈 Tableau Story — 5 Dashboards

### 1. 🏆 Business Performance
> *"Perfect Fitness Rip Deck leads profits, but August 2016 marked peak performance — revenue has been declining since."*

- Top products by total profit
- Monthly profit trend (2015–2017)
- Profit margin bubble chart (color-coded by margin %)
- Highest inventory storage cost by product

### 2. 📦 Inventory Management
> *"Fan Shop is critically understocked vs demand — we're losing sales opportunities."*

- Supply vs Demand bar chart by product
- Inventory Details Table with storage costs
- Overstock and understock identification using average reference line

### 3. 🚢 Shipment Investigation
> *"29% of all orders are delayed — concentrated in Latin America and South/Southeast Asia."*

- World map: Delayed (blue) vs On Time (orange) by country
- 29.05% delay rate highlighted
- Geographic delay pattern identification

### 4. ⚠️ Shipment Delay Details
> *"Caribbean Footwear and Eastern region Pet Shop show the worst delays — 700+ days average."*

- Average shipment delay by Customer Region × Product Department
- Color coded: green = early, red = severely delayed

### 5. ⏱️ Order Fulfillment Days
> *"Sporting Goods takes 130+ days to fulfill — nearly 3× longer than most categories."*

- Average corrected processing time by product category
- Benchmark comparison across all 49 categories

---

## 🔑 Key Findings

| # | Finding | Metric |
|---|---|---|
| 1 | Overall shipment delay rate | **29.05%** of all orders |
| 2 | Peak profit month | **August 2016** — $134,801 |
| 3 | Highest storage cost product | **Perfect Fitness Rip Deck** (~$75,120) |
| 4 | Worst avg shipment delay | **Caribbean Footwear** (700+ days avg) |
| 5 | Most understocked product | **Fan Shop** — demand far exceeds supply |
| 6 | Top profit market | **LATAM** — $1.18M total |
| 7 | ABC Tier A concentration | Top SKUs drive **~70%** of total profit |
| 8 | Longest fulfillment category | **Sporting Goods** — 130+ days avg |

---

## 💡 Business Recommendations

**1. Protect Tier A Products**  
Perfect Fitness Rip Deck, Field & Stream, and Nike Running Shoe drive 65% of profit. Ensure these are never understocked and prioritize their shipping routes.

**2. Investigate LATAM Logistics**  
LATAM is the highest-profit market but also has concentrated shipment delays. A 10% reduction in LATAM delays could materially improve revenue.

**3. Review the First Class / Same Day Delay Paradox**  
Premium shipping modes show higher delay rates than Standard Class — this suggests a routing or capacity problem, not a pricing one.

**4. Rebalance Inventory to ABC Tiers**  
Fan Shop (understocked A-tier) needs reallocation. Redistribute warehouse space from C-tier overstock to high-demand A-tier products.

**5. Audit Anomalous Processing Times**  
8.9% of orders show negative processing times. Root-cause investigation needed — timezone mismatch or data entry errors?

---

## 📌 Acknowledgement

This project was inspired by a DataCamp competition focused on real-world supply chain analytics. Dataset sourced from DataCamp's public competition resources.
