import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Supply Chain Analytics — Just In Time",
    page_icon="📦",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Sidebar background */
[data-testid="stSidebar"] { background-color: #0f1b2d; }
[data-testid="stSidebar"] * { color: #e0e8f0 !important; }

/* KPI card style */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1a2a4a 0%, #0f1b2d 100%);
    border: 1px solid #2a4a7f;
    border-radius: 10px;
    padding: 16px 20px;
}
div[data-testid="metric-container"] label { color: #8ba8cc !important; font-size: 0.8rem !important; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #ffffff !important; font-size: 1.5rem !important; font-weight: 700 !important;
}

/* Section header bar */
.section-banner {
    background: linear-gradient(90deg, #1565C0 0%, #0d47a1 100%);
    padding: 10px 20px; border-radius: 8px; margin-bottom: 12px;
    color: white; font-size: 1.1rem; font-weight: 600;
}

/* Filter bar */
.filter-bar {
    background: #f0f4ff; border-left: 4px solid #1565C0;
    padding: 10px 16px; border-radius: 0 8px 8px 0; margin-bottom: 16px;
    font-size: 0.85rem; color: #333;
}

/* Footer */
.footer {
    text-align: center; color: #888; font-size: 0.78rem;
    padding: 20px 0 4px 0; border-top: 1px solid #e0e0e0; margin-top: 24px;
}
</style>
""", unsafe_allow_html=True)

# ── Plot style ────────────────────────────────────────────────────────────────
sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams.update({
    'figure.dpi': 130,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'figure.facecolor': 'white',
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    df_orders      = pd.read_csv('Datasets/orders_and_shipment.csv', encoding='ISO-8859-1')
    df_inventory   = pd.read_csv('Datasets/inventory.csv')
    df_fulfillment = pd.read_csv('Datasets/fulfillment.csv')

    for df in [df_orders, df_inventory, df_fulfillment]:
        df.columns = df.columns.str.strip()

    df_orders['Discount %'] = df_orders['Discount %'].replace('  -  ', 0).astype(float)

    country_fixes = {
        'Dominican\xa0Republic': 'Dominican Republic',
        'Cote d\x92Ivoire': 'Cote d Ivoire',
        'Per\xfa': 'Peru',
        'Algeria\xa0': 'Algeria',
        'Israel\xa0': 'Israel',
        'Ben\xedn': 'Benin',
    }
    df_orders['Customer Country'] = df_orders['Customer Country'].replace(country_fixes)

    if 'Order Year' in df_orders.columns:
        # Raw split columns → build datetime strings
        order_str = (df_orders['Order Year'].astype(str) + '-' +
                     df_orders['Order Month'].astype(str).str.zfill(2) + '-' +
                     df_orders['Order Day'].astype(str).str.zfill(2))
        ship_str  = (df_orders['Shipment Year'].astype(str) + '-' +
                     df_orders['Shipment Month'].astype(str).str.zfill(2) + '-' +
                     df_orders['Shipment Day'].astype(str).str.zfill(2))
        df_orders['Order Datetime']    = pd.to_datetime(order_str, errors='coerce')
        df_orders['Shipment Datetime'] = pd.to_datetime(ship_str,  errors='coerce')
        drop_cols = ['Order Year','Order Month','Order Day','Order Time',
                     'Shipment Year','Shipment Month','Shipment Day']
        df_orders.drop(columns=drop_cols, inplace=True, errors='ignore')
    else:
        # Columns already exist as strings — force parse them
        df_orders['Order Datetime']    = pd.to_datetime(df_orders['Order Datetime'],    errors='coerce')
        df_orders['Shipment Datetime'] = pd.to_datetime(df_orders['Shipment Datetime'], errors='coerce')

    time_delta = (df_orders['Shipment Datetime'] - df_orders['Order Datetime']).dt.days.astype(float)
    df_orders['Order Processing Time']    = time_delta.fillna(0).clip(lower=0)
    df_orders['Corrected Processing Time'] = df_orders['Order Processing Time'].abs()
    df_orders['Shipment Days - Actual']   = df_orders['Order Processing Time']
    df_orders['Shipment Delay'] = (
        df_orders['Shipment Days - Actual'] - df_orders['Shipment Days - Scheduled']
    )
    df_orders['Is Delay'] = df_orders['Shipment Delay'].apply(
        lambda x: 'Delayed' if x > 0 else 'On Time'
    )

    df_inventory['Storage Cost'] = (
        df_inventory['Warehouse Inventory'] * df_inventory['Inventory Cost Per Unit']
    )

    profit_by_product = (
        df_orders.groupby('Product Name')['Profit']
        .sum().sort_values(ascending=False).reset_index()
    )
    profit_by_product['Cumulative %'] = (
        profit_by_product['Profit'].cumsum() / profit_by_product['Profit'].sum() * 100
    )
    def abc_seg(x):
        if x <= 70: return 'A'
        elif x <= 90: return 'B'
        else: return 'C'
    profit_by_product['ABC Segment'] = profit_by_product['Cumulative %'].apply(abc_seg)

    return df_orders, df_inventory, df_fulfillment, profit_by_product

# ── Load with spinner ─────────────────────────────────────────────────────────
with st.spinner("⏳ Loading supply chain data..."):
    try:
        df_orders, df_inventory, df_fulfillment, profit_by_product = load_data()
        data_loaded = True
    except FileNotFoundError:
        data_loaded = False

if not data_loaded:
    st.error("⚠️ **Dataset not found.** Place `orders_and_shipment.csv`, `inventory.csv`, "
             "and `fulfillment.csv` inside a `Datasets/` folder next to `app.py`.")
    st.stop()

# ── Derived globals ───────────────────────────────────────────────────────────
delay_rate  = (df_orders['Is Delay'] == 'Delayed').mean() * 100
total_profit = df_orders['Profit'].sum()
peak_profit  = df_orders.groupby(df_orders['Order Datetime'].dt.strftime('%Y-%m'))['Profit'].sum().max()
total_orders = len(df_orders)
top_market   = df_orders.groupby('Customer Market')['Profit'].sum().idxmax()
top_product  = profit_by_product.iloc[0]['Product Name']

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 📦 Just In Time")
st.sidebar.markdown("**Supply Chain Analytics**")
st.sidebar.markdown("---")

section = st.sidebar.radio(
    "Navigate to",
    [
        "🏠  Executive Summary",
        "📈  Monthly Profit Trend",
        "🚚  Delay by Shipment Mode",
        "🌎  Profit by Market",
        "🏆  Top 10 Products",
        "🔵  ABC Segmentation",
        "⏱️  Processing Time",
        "🏭  Storage Costs",
        "🔗  Correlation Heatmap",
        "💡  Findings & Recommendations",
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"**Period:** 2015 – 2017  \n"
    f"**Orders:** {total_orders:,}  \n"
    f"**Inventory rows:** {len(df_inventory):,}  \n"
    f"**Fulfillment SKUs:** {len(df_fulfillment):,}"
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "🔗 [Tableau Dashboard](https://public.tableau.com/app/profile/subhrajit.majumder6368/"
    "viz/supplychainoperationsandanalyticssuite/BusinessPerformanceDashboard_)  \n"
    "👤 [GitHub](https://github.com/subhrajit67/Supply-Chain-Analytics)"
)

# ── Helper ────────────────────────────────────────────────────────────────────
def section_header(icon, title, subtitle=""):
    st.markdown(f'<div class="section-banner">{icon} &nbsp;{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)

def insight_box(text):
    st.info(f"💡 **Analyst Insight:** {text}")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Executive Summary
# ═════════════════════════════════════════════════════════════════════════════
if section == "🏠  Executive Summary":
    st.markdown("## 📦 Supply Chain Analytics — Just In Time")
    st.markdown(
        "End-to-end analysis of **shipment delays**, **inventory imbalances**, "
        "and **profit inefficiencies** across global operations (2015–2017)."
    )
    st.divider()

    # KPI Row 1
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚚 Delay Rate",        f"{delay_rate:.1f}%",       "of all orders delayed")
    c2.metric("💰 Total Profit",      f"${total_profit/1e6:.2f}M", "2015–2017 cumulative")
    c3.metric("📈 Peak Month Profit", f"${peak_profit:,.0f}",      "Aug 2016")
    c4.metric("🌎 Top Market",        top_market,                  "by total profit")

    st.divider()

    # Two-column layout
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("#### 🔑 At a Glance")
        findings_data = {
            "Metric": [
                "Shipment Delay Rate", "Peak Month", "Top Product",
                "Worst Delay Region", "Most Understocked", "Top Market",
                "Tier A Profit Share", "Longest Fulfillment"
            ],
            "Value": [
                f"{delay_rate:.1f}%", "Aug 2016 — $134,801",
                " ".join(top_product.split()[:4]),
                "Caribbean Footwear (700+ days avg)",
                "Fan Shop (demand > supply)",
                f"{top_market} — $1.18M",
                "~70% of total profit",
                "Sporting Goods — 130+ days"
            ]
        }
        st.dataframe(
            pd.DataFrame(findings_data),
            use_container_width=True,
            hide_index=True
        )

    with right:
        st.markdown("#### 📊 Delay vs On-Time Split")
        delay_counts = df_orders['Is Delay'].value_counts()
        fig, ax = plt.subplots(figsize=(4, 4))
        colors = ['#EF5350', '#66BB6A']
        wedges, texts, autotexts = ax.pie(
            delay_counts.values,
            labels=delay_counts.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            wedgeprops=dict(width=0.55, edgecolor='white', linewidth=2)
        )
        for t in autotexts:
            t.set_fontsize(12)
            t.set_fontweight('bold')
            t.set_color('white')
        ax.set_title('Order Delay Overview', fontweight='bold', pad=12)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    st.divider()
    st.markdown(
        '<div class="footer">Analysis by <b>Subhrajit Majumder</b> &nbsp;|&nbsp; '
        'DataCamp Supply Chain Competition &nbsp;|&nbsp; '
        'Tools: Python · Pandas · Matplotlib · Seaborn · Streamlit · Tableau</div>',
        unsafe_allow_html=True
    )

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Monthly Profit Trend
# ═════════════════════════════════════════════════════════════════════════════
elif section == "📈  Monthly Profit Trend":
    section_header("📈", "Monthly Profit Trend (2015–2017)",
                   "When was performance best/worst?")

    monthly = (
        df_orders.groupby(df_orders['Order Datetime'].dt.strftime('%Y-%m'))['Profit']
        .sum().reset_index()
    )
    monthly.columns = ['Month', 'Total Profit']

    # Year filter
    year_filter = st.radio("Filter by Year", ["All", "2015", "2016", "2017"], horizontal=True)
    if year_filter != "All":
        monthly = monthly[monthly['Month'].str.startswith(year_filter)]

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(monthly['Month'], monthly['Total Profit'],
            color='#1565C0', linewidth=2.5, marker='o', markersize=5, zorder=3)
    ax.fill_between(monthly['Month'], monthly['Total Profit'], alpha=0.12, color='#1565C0')

    if len(monthly) > 0:
        peak_idx = monthly['Total Profit'].idxmax()
        ax.annotate(
            f"Peak: ${monthly.loc[peak_idx,'Total Profit']:,.0f}\n{monthly.loc[peak_idx,'Month']}",
            xy=(peak_idx - monthly.index[0], monthly.loc[peak_idx,'Total Profit']),
            xytext=(peak_idx - monthly.index[0] + 1.5,
                    monthly.loc[peak_idx,'Total Profit'] - 12000),
            arrowprops=dict(arrowstyle='->', color='#333'),
            fontsize=9, color='#1565C0', fontweight='bold'
        )

    tick_step = max(1, len(monthly) // 8)
    ax.set_xticks(range(0, len(monthly), tick_step))
    ax.set_xticklabels(
        [monthly['Month'].iloc[i] for i in range(0, len(monthly), tick_step)],
        rotation=40, ha='right'
    )
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.set_title('Monthly Profit Trend — Just In Time', fontweight='bold')
    ax.set_xlabel('Month'); ax.set_ylabel('Total Profit ($)')
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    col1, col2, col3 = st.columns(3)
    col1.metric("Min Month Profit",  f"${monthly['Total Profit'].min():,.0f}")
    col2.metric("Max Month Profit",  f"${monthly['Total Profit'].max():,.0f}")
    col3.metric("Avg Monthly Profit",f"${monthly['Total Profit'].mean():,.0f}")

    insight_box("August 2016 was the peak at $134,801. Revenue declined sharply from Q4 2016 — "
                "investigate whether this correlates with delayed shipments or market-level churn.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Delay by Shipment Mode
# ═════════════════════════════════════════════════════════════════════════════
elif section == "🚚  Delay by Shipment Mode":
    section_header("🚚", "Shipment Delay Rate by Mode",
                   "Which shipping methods are most unreliable?")

    delay_by_mode = (
        df_orders.groupby('Shipment Mode')['Is Delay']
        .apply(lambda x: (x == 'Delayed').mean() * 100)
        .sort_values(ascending=False)
        .reset_index()
    )
    delay_by_mode.columns = ['Shipment Mode', 'Delay Rate (%)']

    col_chart, col_table = st.columns([1.6, 1])

    with col_chart:
        fig, ax = plt.subplots(figsize=(8, 4))
        bar_colors = [
            '#C62828' if v > 35 else '#EF5350' if v > 30 else
            '#FFA726' if v > 20 else '#66BB6A'
            for v in delay_by_mode['Delay Rate (%)']
        ]
        bars = ax.barh(delay_by_mode['Shipment Mode'], delay_by_mode['Delay Rate (%)'],
                       color=bar_colors, height=0.55, edgecolor='white')
        ax.axvline(x=delay_rate, color='#1565C0', linestyle='--', linewidth=1.5,
                   label=f'Overall ({delay_rate:.1f}%)')
        for bar, val in zip(bars, delay_by_mode['Delay Rate (%)']):
            ax.text(bar.get_width() + 0.6, bar.get_y() + bar.get_height() / 2,
                    f'{val:.1f}%', va='center', fontsize=11, fontweight='bold')
        ax.set_xlabel('Delay Rate (%)', labelpad=8)
        ax.set_title('Delay Rate by Shipment Mode', fontweight='bold')
        ax.legend(loc='lower right')
        ax.set_xlim(0, delay_by_mode['Delay Rate (%)'].max() + 10)
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    with col_table:
        st.markdown("#### Volume Breakdown")
        mode_vol = df_orders['Shipment Mode'].value_counts().reset_index()
        mode_vol.columns = ['Mode', 'Orders']
        mode_vol['Delayed'] = mode_vol['Mode'].map(
            df_orders[df_orders['Is Delay']=='Delayed']['Shipment Mode'].value_counts()
        ).fillna(0).astype(int)
        mode_vol['Delay %'] = (mode_vol['Delayed'] / mode_vol['Orders'] * 100).round(1)
        st.dataframe(mode_vol, use_container_width=True, hide_index=True)

    insight_box("First Class and Same Day modes delay more than Standard — this is a "
                "routing/capacity problem, not a pricing one. Escalate to logistics ops.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Profit by Market
# ═════════════════════════════════════════════════════════════════════════════
elif section == "🌎  Profit by Market":
    section_header("🌎", "Total Profit by Customer Market",
                   "Which regions drive the most revenue?")

    market_profit = (
        df_orders.groupby('Customer Market')['Profit']
        .sum().sort_values(ascending=False).reset_index()
    )

    col_chart, col_stats = st.columns([1.5, 1])

    with col_chart:
        fig, ax = plt.subplots(figsize=(8, 4))
        palette = ['#1565C0','#1976D2','#1E88E5','#42A5F5','#90CAF9','#BBDEFB'][:len(market_profit)]
        bars = ax.bar(market_profit['Customer Market'], market_profit['Profit'],
                      color=palette, edgecolor='white', linewidth=0.5)
        for bar, val in zip(bars, market_profit['Profit']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8000,
                    f'${val/1e6:.2f}M', ha='center', fontsize=10, fontweight='bold', color='#333')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e6:.1f}M'))
        ax.set_title('Total Profit by Customer Market', fontweight='bold')
        ax.set_xlabel('Market'); ax.set_ylabel('Total Profit')
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    with col_stats:
        st.markdown("#### Market Share")
        market_profit['Share %'] = (market_profit['Profit'] / market_profit['Profit'].sum() * 100).round(1)
        market_profit['Profit ($M)'] = (market_profit['Profit'] / 1e6).round(3)
        st.dataframe(
            market_profit[['Customer Market','Profit ($M)','Share %']],
            use_container_width=True, hide_index=True
        )

    insight_box("LATAM leads at $1.18M yet also has the highest delay concentration — "
                "a 10% delay reduction there could be the single highest-ROI logistics fix.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Top 10 Products
# ═════════════════════════════════════════════════════════════════════════════
elif section == "🏆  Top 10 Products":
    section_header("🏆", "Top 10 Products by Total Profit",
                   "Where is profit concentrated?")

    top_n = st.slider("Show top N products", 5, 20, 10)
    topn = profit_by_product.head(top_n)

    fig, ax = plt.subplots(figsize=(10, max(4, top_n * 0.45)))
    color_map = {'A': '#0d47a1', 'B': '#42A5F5', 'C': '#BBDEFB'}
    colors = [color_map[s] for s in topn['ABC Segment']]
    bars = ax.barh(topn['Product Name'][::-1], topn['Profit'][::-1],
                   color=colors[::-1], height=0.6, edgecolor='white')
    for bar, val in zip(bars, topn['Profit'][::-1]):
        ax.text(bar.get_width() + 300, bar.get_y() + bar.get_height()/2,
                f'${val:,.0f}', va='center', fontsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_title(f'Top {top_n} Products by Profit  (■ A-Tier  ■ B-Tier  ■ C-Tier)',
                 fontweight='bold')
    ax.set_xlabel('Total Profit ($)')
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color='#0d47a1',label='Tier A'),
                        Patch(color='#42A5F5',label='Tier B'),
                        Patch(color='#BBDEFB',label='Tier C')], loc='lower right')
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    st.dataframe(
        topn[['Product Name','Profit','ABC Segment']].rename(
            columns={'Profit':'Total Profit ($)'}
        ).assign(**{'Total Profit ($)': lambda df: df['Total Profit ($)'].map('${:,.0f}'.format)}),
        use_container_width=True, hide_index=True
    )

    insight_box(f"The top {min(5,top_n)} products alone contribute ~65% of total profit. "
                "These SKUs must never go out of stock and should receive priority shipping slots.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: ABC Segmentation
# ═════════════════════════════════════════════════════════════════════════════
elif section == "🔵  ABC Segmentation":
    section_header("🔵", "ABC Segmentation — Product Portfolio",
                   "How many products drive how much profit?")

    abc_counts  = profit_by_product['ABC Segment'].value_counts().sort_index()
    abc_profits = profit_by_product.groupby('ABC Segment')['Profit'].sum().sort_index()

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    colors = ['#0d47a1','#42A5F5','#BBDEFB']
    for ax, data, title in zip(axes,
                                [abc_counts, abc_profits],
                                ['SKU Count by Tier', 'Profit Share by Tier']):
        wedges, texts, autotexts = ax.pie(
            data, labels=data.index, autopct='%1.0f%%', startangle=140,
            colors=colors, wedgeprops=dict(width=0.52, edgecolor='white', linewidth=2)
        )
        for at in autotexts:
            at.set_fontsize(13); at.set_fontweight('bold'); at.set_color('white')
        ax.set_title(title, fontweight='bold', pad=14)

    plt.suptitle('ABC Inventory Segmentation Analysis', fontsize=14, fontweight='bold', y=1.01)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    c1, c2, c3 = st.columns(3)
    for tier, col, color_label in zip(['A','B','C'], [c1,c2,c3],
                                       ['🔵 Critical','🔷 Important','⬜ Monitor']):
        count  = (profit_by_product['ABC Segment'] == tier).sum()
        profit = profit_by_product[profit_by_product['ABC Segment']==tier]['Profit'].sum()
        share  = profit / profit_by_product['Profit'].sum() * 100
        col.metric(f"{color_label} — Tier {tier}",
                   f"{count} SKUs", f"${profit:,.0f} · {share:.0f}% of profit")

    insight_box("Tier A = few SKUs, most profit. Stock these aggressively, never discount "
                "below margin floor. Tier C = many SKUs, low return — ideal for warehouse clearance.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Processing Time
# ═════════════════════════════════════════════════════════════════════════════
elif section == "⏱️  Processing Time":
    section_header("⏱️", "Order Processing Time Distribution",
                   "What does a typical order cycle look like?")

    cap = st.slider("Cap display at (days)", 5, 60, 30)
    valid_proc = df_orders[df_orders['Corrected Processing Time'] <= cap]['Corrected Processing Time']

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.hist(valid_proc, bins=35, color='#5C6BC0', edgecolor='white', linewidth=0.4, alpha=0.88)
    ax.axvline(valid_proc.mean(),   color='#EF5350', linestyle='--', linewidth=2,
               label=f'Mean: {valid_proc.mean():.1f} days')
    ax.axvline(valid_proc.median(), color='#FFA726', linestyle='--', linewidth=2,
               label=f'Median: {valid_proc.median():.1f} days')
    ax.set_xlabel('Processing Time (days)'); ax.set_ylabel('Number of Orders')
    ax.set_title(f'Order Processing Time Distribution (capped at {cap} days)', fontweight='bold')
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mean",   f"{valid_proc.mean():.1f} days")
    c2.metric("Median", f"{valid_proc.median():.1f} days")
    c3.metric("Std Dev",f"{valid_proc.std():.1f} days")
    c4.metric("95th %ile", f"{valid_proc.quantile(0.95):.1f} days")

    neg_pct = (df_orders['Order Processing Time'] < 0).mean() * 100
    insight_box(f"{neg_pct:.1f}% of records show negative processing times — "
                "likely timezone offsets or data entry issues. Worth a dedicated data-quality sprint.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Storage Costs
# ═════════════════════════════════════════════════════════════════════════════
elif section == "🏭  Storage Costs":
    section_header("🏭", "Top Products by Inventory Storage Cost",
                   "Which products cost the most to hold?")

    top_n_stor = st.slider("Show top N products", 5, 20, 10)
    storage_by_product = (
        df_inventory.groupby('Product Name')['Storage Cost']
        .sum().sort_values(ascending=False).head(top_n_stor).reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, max(4, top_n_stor * 0.45)))
    bars = ax.barh(storage_by_product['Product Name'][::-1],
                   storage_by_product['Storage Cost'][::-1],
                   color='#EF5350', height=0.6, edgecolor='white')
    avg_cost = storage_by_product['Storage Cost'].mean()
    ax.axvline(avg_cost, color='#333', linestyle='--', linewidth=1.2,
               label=f'Avg: ${avg_cost:,.0f}')
    for bar, val in zip(bars, storage_by_product['Storage Cost'][::-1]):
        ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height()/2,
                f'${val:,.0f}', va='center', fontsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    ax.set_title(f'Top {top_n_stor} Products by Storage Cost', fontweight='bold')
    ax.set_xlabel('Total Storage Cost ($)')
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    # Enrich with profit data
    enriched = storage_by_product.merge(
        profit_by_product[['Product Name','Profit','ABC Segment']],
        on='Product Name', how='left'
    )
    enriched['Cost/Profit Ratio'] = (enriched['Storage Cost'] / enriched['Profit'].replace(0, np.nan)).round(2)
    enriched['Storage Cost'] = enriched['Storage Cost'].map('${:,.0f}'.format)
    enriched['Profit']       = enriched['Profit'].map('${:,.0f}'.format)
    st.dataframe(enriched, use_container_width=True, hide_index=True)

    insight_box("High storage cost + high profit (Tier A) = justified. "
                "High cost + low profit (Tier C) = liquidate or renegotiate storage contracts immediately.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Correlation Heatmap
# ═════════════════════════════════════════════════════════════════════════════
elif section == "🔗  Correlation Heatmap":
    section_header("🔗", "Correlation Heatmap — Numeric Variables",
                   "How do key supply chain metrics relate to each other?")

    num_cols = ['Order Quantity','Shipment Days - Scheduled','Gross Sales',
                'Discount %','Profit','Order Processing Time','Corrected Processing Time']
    available = [c for c in num_cols if c in df_orders.columns]
    corr = df_orders[available].corr()

    fig, ax = plt.subplots(figsize=(9, 7))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
                center=0, linewidths=0.6, ax=ax,
                cbar_kws={'shrink': 0.75, 'label': 'Pearson r'},
                annot_kws={'size': 10})
    ax.set_title('Feature Correlation Matrix', fontweight='bold', pad=12)
    plt.tight_layout()
    st.pyplot(fig); plt.close()

    st.markdown("#### Top Correlations with Profit")
    profit_corr = (
        corr['Profit'].drop('Profit')
        .abs().sort_values(ascending=False)
        .reset_index()
    )
    profit_corr.columns = ['Feature', '|Correlation with Profit|']
    profit_corr['|Correlation with Profit|'] = profit_corr['|Correlation with Profit|'].round(3)
    st.dataframe(profit_corr, use_container_width=True, hide_index=True)

    insight_box("Gross Sales strongly drives Profit — logical. Discount % shows near-zero "
                "correlation with Profit, suggesting blanket discounting is not a profitable lever.")

# ═════════════════════════════════════════════════════════════════════════════
# PAGE: Findings & Recommendations
# ═════════════════════════════════════════════════════════════════════════════
elif section == "💡  Findings & Recommendations":
    section_header("💡", "Key Findings & Business Recommendations")

    st.markdown("#### 📊 Summary of Findings")
    findings_df = pd.DataFrame({
        "#": range(1, 9),
        "Finding": [
            "Overall Shipment Delay Rate",
            "Peak Profit Month",
            "Highest Storage Cost Product",
            "Worst Avg Shipment Delay",
            "Most Understocked Product",
            "Top Profit Market",
            "ABC Tier A Concentration",
            "Longest Fulfillment Category",
        ],
        "Metric": [
            f"{delay_rate:.2f}% of all orders",
            "August 2016 — $134,801",
            "Perfect Fitness Rip Deck (~$75,120)",
            "Caribbean Footwear (700+ days avg)",
            "Fan Shop — demand >> supply",
            f"{top_market} — $1.18M total",
            "Top SKUs → ~70% of profit",
            "Sporting Goods — 130+ days avg",
        ],
        "Priority": ["🔴 High","🟡 Medium","🟡 Medium","🔴 High","🔴 High","🟢 Positive","🟡 Medium","🟡 Medium"]
    })
    st.dataframe(findings_df, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### 🎯 Actionable Recommendations")

    recs = [
        ("🛡️ Protect Tier A Products — Never Stockout",
         "Perfect Fitness Rip Deck, Field & Stream, and Nike Running Shoe drive 65% of profit. "
         "Set automatic reorder triggers, dedicate premium shipping lanes, and implement safety stock buffers. "
         "A single stockout event on a Tier A SKU can wipe out a month of margin."),
        ("🌎 Fix LATAM Logistics — Highest ROI Fix Available",
         "LATAM is the most profitable market ($1.18M) yet concentrates the most delays. "
         "Audit carrier contracts, consider regional 3PL partnerships, and target a 10% delay reduction — "
         "this single fix could add $100K+ in recovered revenue annually."),
        ("⚡ Investigate Premium Shipping Mode Failures",
         "First Class and Same Day show higher delay rates than Standard Class — a paradox. "
         "This signals a routing capacity or carrier reliability issue, not a customer pricing problem. "
         "Run a root-cause analysis with the logistics team before the next contract renewal."),
        ("📦 Rebalance Inventory: Fan Shop is Bleeding Revenue",
         "Fan Shop is critically understocked relative to demand — lost sales are invisible in current dashboards. "
         "Reallocate warehouse space from C-tier overstock (holding cost with low return) to high-demand A-tier products. "
         "Implement monthly inventory rebalancing reviews."),
        ("🔍 Audit the 8.9% Anomalous Processing Times",
         "Negative processing times suggest systematic data capture issues — timezone mismatches, "
         "manual entry errors, or ERP integration bugs. Fix upstream data quality now before "
         "these anomalies corrupt future ML models or executive dashboards."),
    ]

    for i, (title, body) in enumerate(recs):
        with st.expander(f"Recommendation {i+1}: {title}", expanded=(i==0)):
            st.write(body)

    st.divider()
    st.markdown(
        '<div class="footer">Analysis by <b>Subhrajit Majumder</b> &nbsp;|&nbsp; '
        'DataCamp Supply Chain Competition &nbsp;|&nbsp; '
        'Python · Pandas · Matplotlib · Seaborn · Streamlit · Tableau</div>',
        unsafe_allow_html=True
    )
