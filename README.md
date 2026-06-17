# 📦 Supply Chain Analytics — Moving from Complexity to Clarity

> End-to-end supply chain analytics project for **Just In Time**, a global e-commerce company.  
> Identifies shipment delays, inventory imbalances, and profit inefficiencies — and delivers data-driven solutions through an interactive Streamlit web app and Tableau story dashboards.

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Pandas-Data%20Wrangling-150458?logo=pandas&logoColor=white" />
  <img src="https://img.shields.io/badge/Tableau-Dashboard-E97627?logo=tableau&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Live-brightgreen" />
</p>

**🔗 Live Streamlit App:** [View App](https://supply-chain-analytics-tpu5f9ifsb7xus9r7hg5q2.streamlit.app/) 

**🔗 Tableau Story Dashboard:** [View on Tableau Public](https://public.tableau.com/app/profile/subhrajit.majumder6368/viz/supplychainoperationsandanalyticssuite/BusinessPerformanceDashboard_)

---

## 🎯 Problem Statement

Just In Time's supply chain is losing revenue through three compounding problems:
- **29% of all orders are delayed** — with no visibility into which shipping modes or regions are responsible
- **Inventory is misallocated** — high-demand products are understocked while slow-movers tie up warehouse capital
- **Profit is heavily concentrated** — the top few SKUs drive most revenue, yet they receive no special protection

This project answers: *where are the leaks, how large are they, and what should the business do about them?*

---

## 🏆 Key Results

| # | Finding | Impact |
|---|---|---|
| 1 | Overall shipment delay rate | **29.05%** of all orders |
| 2 | Peak profit month | **August 2016 — $134,801** |
| 3 | Highest storage cost product | **Perfect Fitness Rip Deck** (~$75,120) |
| 4 | Worst avg shipment delay | **Caribbean Footwear** (700+ days avg) |
| 5 | Most understocked product | **Fan Shop** — demand far exceeds supply |
| 6 | Top profit market | **LATAM — $1.18M** total |
| 7 | ABC Tier A concentration | Top SKUs drive **~70%** of total profit |
| 8 | Longest fulfillment category | **Sporting Goods — 130+ days** avg |

---

## 🛠️ Tools & Technologies

| Tool | Purpose |
|---|---|
| Python 3.11 (Pandas, NumPy) | Data cleaning, preprocessing, feature engineering |
| Matplotlib & Seaborn | EDA visualizations |
| Streamlit | Interactive web application |
| Tableau Public | Story dashboards for business stakeholders |
| Jupyter Notebook | Exploratory analysis & documentation |

---

## 📁 Project Structure

```
Supply-Chain-Analytics/
│
├── Datasets/
│   ├── orders_and_shipment.csv     # 30,871 rows — orders, shipment mode, profit
│   ├── inventory.csv               # 4,200 rows — warehouse inventory by product
│   └── fulfillment.csv             # 118 rows — avg fulfillment days per product
│
├── plots/                          # Auto-generated EDA charts (8 total)
│
├── app.py                          # ← Streamlit web application
├── Supply_Chain_Analytics.ipynb    # ← Main analysis notebook
├── .python-version                 # Python 3.11 pin for Streamlit Cloud
├── requirements.txt                # Python dependencies
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

# 3a. Run the Streamlit app
streamlit run app.py

# 3b. Or run the analysis notebook
jupyter notebook Supply_Chain_Analytics.ipynb
```

> All notebook cells run top-to-bottom. Cleaned CSVs and EDA plots are exported automatically.

---

## 📊 Dataset Overview

Three datasets covering **2015–2017**:

| Dataset | Rows | Description |
|---|---|---|
| `orders_and_shipment.csv` | 30,871 | Order details, customer info, shipment mode, profit, discount |
| `inventory.csv` | 4,200 | Monthly warehouse inventory per product + storage cost per unit |
| `fulfillment.csv` | 118 | Average fulfillment days per product |

---

## 🔧 Data Preprocessing & Feature Engineering

| Step | What Was Done |
|---|---|
| Data Quality Check | Null values, duplicates, statistical summary |
| Column Cleaning | Stripped whitespace from all headers |
| Discount Fix | Replaced `'  -  '` string values with `0` in `Discount %` |
| Country Fix | Resolved encoding artefacts (`\xa0`, `\x92`, etc.) in country names |
| Date Engineering | Merged year/month/day columns → `Order Datetime`, `Shipment Datetime` |
| Processing Time | `Shipment Datetime − Order Datetime`; negatives clipped to 0 |
| Shipment Delay | `Actual days − Scheduled days` + binary `Is Delay` flag |
| Storage Cost | `Warehouse Inventory × Inventory Cost Per Unit` |
| ABC Segmentation | Products classified A/B/C by cumulative profit (A ≤ 70%, B ≤ 90%, C = rest) |
| Export | 3 cleaned CSVs exported for Tableau ingestion |

---

## 📈 Exploratory Data Analysis — 8 Visualizations

| Chart | Business Question Answered |
|---|---|
| Monthly Profit Trend | When was performance best/worst? |
| Delay Rate by Shipment Mode | Which shipping methods are most unreliable? |
| Profit by Customer Market | Which regions drive the most revenue? |
| Top 10 Products by Profit | Where is profit concentrated? |
| ABC Segmentation Donuts | How many SKUs drive how much of the profit? |
| Processing Time Distribution | What does a typical order cycle look like? |
| Top 10 Storage Cost Products | Which products cost the most to hold? |
| Correlation Heatmap | How do numeric supply chain variables relate? |

---

## 📊 Tableau Story — 5 Dashboards

### 1. 🏆 Business Performance
> *"Perfect Fitness Rip Deck leads profits, but August 2016 marked peak performance — revenue has been declining since."*

### 2. 📦 Inventory Management
> *"Fan Shop is critically understocked vs demand — we're losing sales opportunities."*

### 3. 🚢 Shipment Investigation
> *"29% of all orders are delayed — concentrated in Latin America and South/Southeast Asia."*

### 4. ⚠️ Shipment Delay Details
> *"Caribbean Footwear and Eastern region Pet Shop show the worst delays — 700+ days average."*

### 5. ⏱️ Order Fulfillment Days
> *"Sporting Goods takes 130+ days to fulfill — nearly 3× longer than most categories."*

---

## 💡 Business Recommendations

**1. 🛡️ Protect Tier A Products — Never Stockout**  
Perfect Fitness Rip Deck, Field & Stream, and Nike Running Shoe drive 65% of profit. Set automatic reorder triggers and dedicate premium shipping lanes to these SKUs.

**2. 🌎 Fix LATAM Logistics — Highest ROI Fix Available**  
LATAM is the most profitable market ($1.18M) yet has the most concentrated delays. A 10% delay reduction could recover $100K+ in annual revenue.

**3. ⚡ Investigate the Premium Shipping Delay Paradox**  
First Class and Same Day modes delay more than Standard Class — a carrier reliability or routing capacity issue, not a pricing one. Audit before next contract renewal.

**4. 📦 Rebalance Inventory by ABC Tier**  
Fan Shop (understocked Tier A) needs emergency reallocation. Move warehouse space from Tier C overstock to high-demand Tier A products.

**5. 🔍 Audit Anomalous Processing Times**  
8.9% of orders show negative processing times — likely timezone offsets or ERP data entry errors. Fix upstream data quality before it corrupts future models.

---

## 📌 Acknowledgement

Inspired by a DataCamp competition focused on real-world supply chain analytics. Dataset sourced from DataCamp's public competition resources.

---

*Built by [Subhrajit Majumder](https://github.com/subhrajit67)*
