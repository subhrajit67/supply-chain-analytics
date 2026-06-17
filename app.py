import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import os

warnings.filterwarnings('ignore')

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Analytics — Just In Time",
    page_icon="📦",
    layout="wide"
)

# ── Plot style ────────────────────────────────────────────────────────────────
sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams.update({
    'figure.dpi': 120,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'figure.facecolor': 'white'
})

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📦 Supply Chain Analytics — Just In Time")
st.markdown(
    "End-to-end supply chain analysis covering **shipment delays**, "
    "**inventory imbalances**, and **profit inefficiencies** (2015–2017)."
)
st.markdown(
    "🔗 **[View Full Tableau Story Dashboard](https://public.tableau.com/app/profile/"
    "subhrajit.majumder6368/viz/supplychainoperationsandanalyticssuite/BusinessPerformanceDashboard_)**"
)
st.divider()

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df_orders      = pd.read_csv('Datasets/orders_and_shipment.csv', encoding='ISO-8859-1')
    df_inventory   = pd.read_csv('Datasets/inventory.csv')
    df_fulfillment = pd.read_csv('Datasets/fulfillment.csv')

    # Strip column whitespace
    for df in [df_orders, df_inventory, df_fulfillment]:
        df.columns = df.columns.str.strip()

    # Fix Discount %
    df_orders['Discount %'] = (
        df_orders['Discount %'].replace('  -  ', 0).astype(float)
    )

    # Fix encoding artefacts in country names
    country_fixes = {
        'Dominican\xa0Republic': 'Dominican Republic',
        'Cote d\x92Ivoire'     : 'Cote d Ivoire',
        'Per\xfa'              : 'Peru',
        'Algeria\xa0'          : 'Algeria',
        'Israel\xa0'           : 'Israel',
        'Ben\xedn'             : 'Benin',
    }
    df_orders['Customer Country'] = df_orders['Customer Country'].replace(country_fixes)

    # Build datetime columns
    if 'Order Year' in df_orders.columns:
        order_str = (df_orders['Order Year'].astype(str) + '-' +
                     df_orders['Order Month'].astype(str) + '-' +
                     df_orders['Order Day'].astype(str) + ' ' +
                     df_orders['Order Time'].astype(str))
        df_orders['Order Datetime'] = pd.to_datetime(order_str, errors='coerce')

        ship_str = (df_orders['Shipment Year'].astype(str) + '-' +
                    df_orders['Shipment Month'].astype(str) + '-' +
                    df_orders['Shipment Day'].astype(str) + ' ' +
                    df_orders['Order Time'].astype(str))
        df_orders['Shipment Datetime'] = pd.to_datetime(ship_str, errors='coerce')

        drop_cols = ['Order Year', 'Order Month', 'Order Day', 'Order Time',
                     'Shipment Year', 'Shipment Month', 'Shipment Day']
        df_orders.drop(columns=drop_cols, inplace=True, errors='ignore')

    # Processing time
    df_orders['Shipment Datetime'] = pd.to_datetime(df_orders['Shipment Datetime'])
    df_orders['Order Datetime'] = pd.to_datetime(df_orders['Order Datetime'])
    
    time_delta = (df_orders['Shipment Datetime'] - df_orders['Order Datetime']).to_numpy()
    df_orders['Order Processing Time'] = (time_delta / np.timedelta64(1, 'D')).astype(float)
    df_orders['Order Processing Time'] = df_orders['Order Processing Time'].fillna(0).clip(lower=0)
    df_orders['Corrected Processing Time'] = df_orders['Order Processing Time'].abs()

    # Shipment delay
    df_orders['Shipment Days - Actual'] = df_orders['Order Processing Time']
    df_orders['Shipment Delay'] = (
        df_orders['Shipment Days - Actual'] - df_orders['Shipment Days - Scheduled']
    )
    df_orders['Is Delay'] = df_orders['Shipment Delay'].apply(
        lambda x: 'Delayed' if x > 0 else 'On Time'
    )

    # Storage cost
    df_inventory['Storage Cost'] = (
        df_inventory['Warehouse Inventory'] * df_inventory['Inventory Cost Per Unit']
    )

    # ABC segmentation
    profit_by_product = (
        df_orders.groupby('Product Name')['Profit']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    profit_by_product['Cumulative %'] = (
        profit_by_product['Profit'].cumsum() / profit_by_product['Profit'].sum() * 100
    )
    def abc_segment(cum_pct):
        if cum_pct <= 70: return 'A'
        elif cum_pct <= 90: return 'B'
        else: return 'C'
    profit_by_product['ABC Segment'] = profit_by_product['Cumulative %'].apply(abc_segment)

    return df_orders, df_inventory, df_fulfillment, profit_by_product


# ── Load ──────────────────────────────────────────────────────────────────────
with st.spinner("Loading and processing data..."):
    try:
        df_orders, df_inventory, df_fulfillment, profit_by_product = load_data()
        data_loaded = True
    except FileNotFoundError:
        data_loaded = False

if not data_loaded:
    st.error(
        "⚠️ Dataset files not found. Make sure the `Datasets/` folder with "
        "`orders_and_shipment.csv`, `inventory.csv`, and `fulfillment.csv` "
        "is present in the same directory as `app.py`."
    )
    st.stop()

# ── KPI cards ─────────────────────────────────────────────────────────────────
delay_rate = (df_orders['Is Delay'] == 'Delayed').mean() * 100
peak_profit = df_orders.groupby(df_orders['Order Datetime'].dt.strftime('%Y-%m'))['Profit'].sum().max()
top_market  = df_orders.groupby('Customer Market')['Profit'].sum().idxmax()
top_product = profit_by_product.iloc[0]['Product Name']

col1, col2, col3, col4 = st.columns(4)
col1.metric("🚚 Overall Delay Rate", f"{delay_rate:.1f}%")
col2.metric("📈 Peak Monthly Profit", f"${peak_profit:,.0f}")
col3.metric("🌎 Top Market", top_market)
col4.metric("🏆 Top Product", top_product.split()[:3].__len__() and " ".join(top_product.split()[:3]) + "…")

st.divider()

# ── Sidebar navigation ────────────────────────────────────────────────────────
st.sidebar.title("📊 Navigation")
section = st.sidebar.radio(
    "Go to",
    [
        "1 · Monthly Profit Trend",
        "2 · Delay Rate by Shipment Mode",
        "3 · Profit by Market",
        "4 · Top 10 Products by Profit",
        "5 · ABC Segmentation",
        "6 · Processing Time Distribution",
        "7 · Storage Cost Top 10",
        "8 · Correlation Heatmap",
        "9 · Key Findings & Recommendations",
    ]
)

st.sidebar.divider()
st.sidebar.markdown(
    "**Dataset period:** 2015–2017  \n"
    f"**Orders:** {len(df_orders):,}  \n"
    f"**Inventory records:** {len(df_inventory):,}  \n"
    f"**Fulfillment entries:** {len(df_fulfillment):,}"
)

# ── Chart sections ────────────────────────────────────────────────────────────

# 1. Monthly Profit Trend
if section == "1 · Monthly Profit Trend":
    st.subheader("📈 Monthly Profit Trend (2015–2017)")
    st.caption("When was performance best/worst?")

    monthly_profit = (
        df_orders.groupby(df_orders['Order Datetime'].dt.strftime('%Y-%m'))['Profit']
        .sum()
        .reset_index()
    )
    monthly_profit.columns = ['Month', 'Total Profit']

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(monthly_profit['Month'], monthly_profit['Total Profit'],
            color='#2196F3', linewidth=2, marker='o', markersize=4)
    ax.fill_between(monthly_profit['Month'], monthly_profit['Total Profit'],
                    alpha=0.1, color='#2196F3')

    peak_idx = monthly_profit['Total Profit'].idxmax()
    peak_month = monthly_profit.loc[peak_idx, 'Month']
    peak_val   = monthly_profit.loc[peak_idx, 'Total Profit']
    ax.annotate(
        f"Peak: ${peak_val:,.0f}\n{peak_month}",
        xy=(peak_idx, peak_val),
        xytext=(peak_idx + 2, peak_val - 15000),
        arrowprops=dict(arrowstyle='->', color='gray'),
        fontsize=9, color='#333'
    )

    tick_positions = range(0, len(monthly_profit), 3)
    ax.set_xticks(list(tick_positions))
    ax.set_xticklabels([monthly_profit['Month'].iloc[i] for i in tick_positions], rotation=45)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_title('Monthly Profit Trend — Just In Time (2015–2017)', fontweight='bold')
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Profit')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.info("💡 **Insight:** August 2016 was the peak month at $134,801. Revenue has been declining since — investigate what changed in Q4 2016 onward.")

# 2. Delay Rate by Shipment Mode
elif section == "2 · Delay Rate by Shipment Mode":
    st.subheader("🚚 Shipment Delay Rate by Mode")
    st.caption("Which shipping methods are most delayed?")

    delay_by_mode = (
        df_orders.groupby('Shipment Mode')['Is Delay']
        .apply(lambda x: (x == 'Delayed').mean() * 100)
        .sort_values(ascending=False)
        .reset_index()
    )
    delay_by_mode.columns = ['Shipment Mode', 'Delay Rate (%)']

    fig, ax = plt.subplots(figsize=(8, 4))
    colors = [
        '#EF5350' if v > 30 else '#FFA726' if v > 20 else '#66BB6A'
        for v in delay_by_mode['Delay Rate (%)']
    ]
    bars = ax.barh(delay_by_mode['Shipment Mode'], delay_by_mode['Delay Rate (%)'], color=colors)
    ax.axvline(x=delay_rate, color='red', linestyle='--', linewidth=1.2,
               label=f'Overall Avg Delay ({delay_rate:.1f}%)')
    for bar, val in zip(bars, delay_by_mode['Delay Rate (%)']):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f'{val:.1f}%', va='center', fontsize=10)
    ax.set_xlabel('Delay Rate (%)')
    ax.set_title('Shipment Delay Rate by Mode', fontweight='bold')
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.info("💡 **Insight:** First Class and Same Day modes show the highest delay rates — this is a routing/capacity problem, not a pricing one.")

# 3. Profit by Market
elif section == "3 · Profit by Market":
    st.subheader("🌎 Total Profit by Customer Market")
    st.caption("Which regions drive the most revenue?")

    market_profit = (
        df_orders.groupby('Customer Market')['Profit']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    palette = sns.color_palette('Blues_r', len(market_profit))
    bars = ax.bar(market_profit['Customer Market'], market_profit['Profit'], color=palette)
    for bar, val in zip(bars, market_profit['Profit']):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5000,
                f'${val:,.0f}', ha='center', fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.1f}M'))
    ax.set_title('Total Profit by Customer Market', fontweight='bold')
    ax.set_xlabel('Market')
    ax.set_ylabel('Total Profit')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.info("💡 **Insight:** LATAM is the most profitable market ($1.18M) yet also has concentrated shipment delays — a high-risk, high-reward region.")

# 4. Top 10 Products
elif section == "4 · Top 10 Products by Profit":
    st.subheader("🏆 Top 10 Products by Total Profit")
    st.caption("Where is profit concentrated?")

    top10 = profit_by_product.head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['#1565C0' if s == 'A' else '#42A5F5' if s == 'B' else '#BBDEFB'
              for s in top10['ABC Segment']]
    bars = ax.barh(top10['Product Name'][::-1], top10['Profit'][::-1], color=colors[::-1])
    for bar, val in zip(bars, top10['Profit'][::-1]):
        ax.text(bar.get_width() + 500, bar.get_y() + bar.get_height() / 2,
                f'${val:,.0f}', va='center', fontsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_title('Top 10 Products by Total Profit (A=Dark Blue, B=Mid, C=Light)', fontweight='bold')
    ax.set_xlabel('Total Profit ($)')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.info("💡 **Insight:** The top 5 products alone contribute ~65% of total profit — classic ABC concentration. Never let these go out of stock.")

# 5. ABC Segmentation
elif section == "5 · ABC Segmentation":
    st.subheader("🔵 ABC Segmentation — Product Distribution")
    st.caption("How many products drive how much profit?")

    abc_counts  = profit_by_product['ABC Segment'].value_counts().sort_index()
    abc_profits = profit_by_product.groupby('ABC Segment')['Profit'].sum().sort_index()

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    for ax, data, title in zip(
        axes,
        [abc_counts, abc_profits],
        ['Products by ABC Tier', 'Profit Share by ABC Tier']
    ):
        ax.pie(data, labels=data.index, autopct='%1.0f%%', startangle=140,
               colors=['#1565C0', '#42A5F5', '#BBDEFB'],
               wedgeprops=dict(width=0.5))
        ax.set_title(title, fontweight='bold')

    plt.suptitle('ABC Segmentation Analysis', fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    col1, col2, col3 = st.columns(3)
    for tier, col in zip(['A', 'B', 'C'], [col1, col2, col3]):
        count = (profit_by_product['ABC Segment'] == tier).sum()
        profit = profit_by_product[profit_by_product['ABC Segment'] == tier]['Profit'].sum()
        col.metric(f"Tier {tier} Products", f"{count}", f"${profit:,.0f} profit")

    st.info("💡 **Insight:** Tier A products (few SKUs) generate the majority of profit. Focus inventory, marketing, and logistics on these.")

# 6. Processing Time Distribution
elif section == "6 · Processing Time Distribution":
    st.subheader("⏱️ Order Processing Time Distribution")
    st.caption("What does a typical order cycle look like?")

    valid_proc = df_orders[df_orders['Corrected Processing Time'] <= 30]['Corrected Processing Time']

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.hist(valid_proc, bins=30, color='#5C6BC0', edgecolor='white', linewidth=0.5)
    ax.axvline(valid_proc.mean(),   color='red',    linestyle='--', label=f'Mean: {valid_proc.mean():.1f} days')
    ax.axvline(valid_proc.median(), color='orange', linestyle='--', label=f'Median: {valid_proc.median():.1f} days')
    ax.set_xlabel('Order Processing Time (days)')
    ax.set_ylabel('Number of Orders')
    ax.set_title('Distribution of Order Processing Time (≤30 days)', fontweight='bold')
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    neg_pct = (df_orders['Order Processing Time'] < 0).mean() * 100
    st.info(f"💡 **Insight:** Most orders process in 1–4 days. {neg_pct:.1f}% of orders show anomalous values — likely timezone mismatches or data entry errors needing investigation.")

# 7. Storage Cost
elif section == "7 · Storage Cost Top 10":
    st.subheader("🏭 Top 10 Products by Inventory Storage Cost")
    st.caption("Which products cost the most to hold?")

    storage_by_product = (
        df_inventory.groupby('Product Name')['Storage Cost']
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(storage_by_product['Product Name'][::-1],
                   storage_by_product['Storage Cost'][::-1],
                   color='#EF5350')
    for bar, val in zip(bars, storage_by_product['Storage Cost'][::-1]):
        ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height() / 2,
                f'${val:,.0f}', va='center', fontsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_title('Top 10 Products by Total Inventory Storage Cost', fontweight='bold')
    ax.set_xlabel('Total Storage Cost ($)')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.info("💡 **Insight:** Perfect Fitness Rip Deck leads storage cost at ~$75K. High storage + high profit = worth it. High storage + low profit = immediate review needed.")

# 8. Correlation Heatmap
elif section == "8 · Correlation Heatmap":
    st.subheader("🔗 Correlation Heatmap — Numeric Features")
    st.caption("How do numeric variables relate to each other?")

    num_cols = ['Order Quantity', 'Shipment Days - Scheduled', 'Gross Sales',
                'Discount %', 'Profit', 'Order Processing Time', 'Corrected Processing Time']
    available = [c for c in num_cols if c in df_orders.columns]
    corr = df_orders[available].corr()

    fig, ax = plt.subplots(figsize=(9, 7))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
                center=0, linewidths=0.5, ax=ax, cbar_kws={'shrink': 0.8})
    ax.set_title('Correlation Heatmap — Numeric Features', fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.info("💡 **Insight:** Gross Sales and Profit show strong positive correlation. Discount % has minimal correlation with Profit — discounts alone don't drive profit.")

# 9. Key Findings
elif section == "9 · Key Findings & Recommendations":
    st.subheader("🔑 Key Findings")

    findings = {
        "Overall shipment delay rate": f"**{delay_rate:.2f}%** of all orders",
        "Peak profit month": "**August 2016** — $134,801",
        "Highest storage cost product": "**Perfect Fitness Rip Deck** (~$75,120)",
        "Worst avg shipment delay region": "**Caribbean Footwear** (700+ days avg)",
        "Most understocked product": "**Fan Shop** — demand far exceeds supply",
        "Top profit market": "**LATAM** — $1.18M total",
        "ABC Tier A concentration": "Top SKUs drive **~70%** of total profit",
        "Longest fulfillment category": "**Sporting Goods** — 130+ days avg",
    }
    for finding, metric in findings.items():
        st.markdown(f"- {finding}: {metric}")

    st.divider()
    st.subheader("💡 Business Recommendations")

    recs = [
        ("🛡️ Protect Tier A Products",
         "Perfect Fitness Rip Deck, Field & Stream, and Nike Running Shoe drive 65% of profit. "
         "Ensure these are never understocked and prioritize their shipping routes."),
        ("🌎 Investigate LATAM Logistics",
         "LATAM is the highest-profit market but also has concentrated shipment delays. "
         "A 10% reduction in LATAM delays could materially improve revenue."),
        ("⚡ Review First Class / Same Day Delay Paradox",
         "Premium shipping modes show higher delay rates than Standard Class — "
         "this suggests a routing or capacity problem, not a pricing one."),
        ("📦 Rebalance Inventory to ABC Tiers",
         "Fan Shop (understocked A-tier) needs reallocation. Redistribute warehouse space "
         "from C-tier overstock to high-demand A-tier products."),
        ("🔍 Audit Anomalous Processing Times",
         "8.9% of orders show negative processing times. Root-cause investigation needed — "
         "timezone mismatch or data entry errors?"),
    ]
    for title, body in recs:
        with st.expander(title):
            st.write(body)

    st.divider()
    st.markdown(
        "*Analysis by Subhrajit Majumder | Dataset: DataCamp Supply Chain Competition | "
        "Tools: Python (Pandas, NumPy, Matplotlib, Seaborn) → Tableau*"
    )