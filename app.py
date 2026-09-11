import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Cafe Sales Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* Main background */
    .stApp {
        background-color: #f7f3ef;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #2b211d;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    /* Main title */
    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #3b2922;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 17px;
        color: #76645c;
        margin-bottom: 25px;
    }

    /* KPI Cards */
    .kpi-card {
        background-color: white;
        padding: 22px;
        border-radius: 15px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
        border-left: 5px solid #8b5e3c;
    }

    .kpi-title {
        color: #76645c;
        font-size: 15px;
        font-weight: 600;
    }

    .kpi-value {
        color: #3b2922;
        font-size: 30px;
        font-weight: 800;
        margin-top: 5px;
    }

    /* Section titles */
    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #3b2922;
        margin-top: 20px;
        margin-bottom: 10px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv("dirty_cafe_sales.csv")

    # Replace common dirty values
    dirty_values = [
        "UNKNOWN",
        "Unknown",
        "unknown",
        "ERROR",
        "Error",
        "error",
        "",
        " "
    ]

    df = df.replace(dirty_values, pd.NA)

    # Convert numeric columns
    numeric_columns = [
        "Quantity",
        "Price Per Unit",
        "Total Spent"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Convert date
    df["Transaction Date"] = pd.to_datetime(
        df["Transaction Date"],
        errors="coerce"
    )

    # Remove rows without essential information
    df = df.dropna(
        subset=[
            "Transaction ID",
            "Transaction Date"
        ]
    )

    # Fill categorical missing values
    categorical_columns = [
        "Item",
        "Payment Method",
        "Location"
    ]

    for col in categorical_columns:
        df[col] = df[col].fillna("Unknown")

    # Fill numerical missing values using median
    for col in numeric_columns:
        df[col] = df[col].fillna(df[col].median())

    # Create useful date columns
    df["Year"] = df["Transaction Date"].dt.year
    df["Month"] = df["Transaction Date"].dt.month
    df["Month Name"] = df["Transaction Date"].dt.strftime("%b")

    return df


df = load_data()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">☕ Cafe Sales Dashboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Interactive analysis of cafe transactions, revenue and customer activity'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.markdown("## ☕ Cafe Analytics")

st.sidebar.markdown("---")

# Date filter
min_date = df["Transaction Date"].min().date()
max_date = df["Transaction Date"].max().date()

date_range = st.sidebar.date_input(
    "📅 Transaction Date",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Item filter
items = sorted(df["Item"].dropna().unique())

selected_items = st.sidebar.multiselect(
    "☕ Select Item",
    items,
    default=items
)

# Payment filter
payments = sorted(df["Payment Method"].dropna().unique())

selected_payments = st.sidebar.multiselect(
    "💳 Payment Method",
    payments,
    default=payments
)

# Location filter
locations = sorted(df["Location"].dropna().unique())

selected_locations = st.sidebar.multiselect(
    "📍 Location",
    locations,
    default=locations
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()

if len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    filtered_df = filtered_df[
        (filtered_df["Transaction Date"] >= start_date) &
        (filtered_df["Transaction Date"] <= end_date)
    ]

filtered_df = filtered_df[
    filtered_df["Item"].isin(selected_items)
]

filtered_df = filtered_df[
    filtered_df["Payment Method"].isin(selected_payments)
]

filtered_df = filtered_df[
    filtered_df["Location"].isin(selected_locations)
]


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_revenue = filtered_df["Total Spent"].sum()

total_transactions = filtered_df["Transaction ID"].nunique()

total_items = filtered_df["Quantity"].sum()

average_transaction = (
    total_revenue / total_transactions
    if total_transactions > 0
    else 0
)


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">💰 Total Revenue</div>
            <div class="kpi-value">₹{total_revenue:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">🧾 Transactions</div>
            <div class="kpi-value">{total_transactions:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">📦 Items Sold</div>
            <div class="kpi-value">{total_items:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">💵 Avg Transaction</div>
            <div class="kpi-value">₹{average_transaction:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# REVENUE TREND
# ============================================================

st.markdown(
    '<div class="section-title">📈 Revenue Trend</div>',
    unsafe_allow_html=True
)

daily_sales = (
    filtered_df
    .groupby("Transaction Date", as_index=False)["Total Spent"]
    .sum()
)

fig = px.line(
    daily_sales,
    x="Transaction Date",
    y="Total Spent",
    markers=True,
    title="Daily Revenue"
)

fig.update_layout(
    template="plotly_white",
    xaxis_title="Date",
    yaxis_title="Revenue",
    hovermode="x unified"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# TWO COLUMN CHART SECTION
# ============================================================

col1, col2 = st.columns(2)


# ------------------------------------------------------------
# SALES BY ITEM
# ------------------------------------------------------------

with col1:

    st.markdown(
        '<div class="section-title">☕ Sales by Item</div>',
        unsafe_allow_html=True
    )

    item_sales = (
        filtered_df
        .groupby("Item", as_index=False)["Total Spent"]
        .sum()
        .sort_values("Total Spent", ascending=False)
    )

    fig = px.bar(
        item_sales,
        x="Item",
        y="Total Spent",
        text_auto=".2s",
        title="Revenue by Product"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Item",
        yaxis_title="Revenue"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# PAYMENT METHOD
# ------------------------------------------------------------

with col2:

    st.markdown(
        '<div class="section-title">💳 Payment Methods</div>',
        unsafe_allow_html=True
    )

    payment_data = (
        filtered_df
        .groupby("Payment Method", as_index=False)["Total Spent"]
        .sum()
    )

    fig = px.pie(
        payment_data,
        names="Payment Method",
        values="Total Spent",
        hole=0.45,
        title="Revenue by Payment Method"
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# MONTHLY ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">📅 Monthly Performance</div>',
    unsafe_allow_html=True
)

monthly_sales = (
    filtered_df
    .groupby(["Year", "Month"], as_index=False)["Total Spent"]
    .sum()
)

monthly_sales["Month Label"] = (
    monthly_sales["Year"].astype(str)
    + "-"
    + monthly_sales["Month"].astype(str).str.zfill(2)
)

fig = px.bar(
    monthly_sales,
    x="Month Label",
    y="Total Spent",
    text_auto=".2s",
    title="Monthly Revenue"
)

fig.update_layout(
    template="plotly_white",
    xaxis_title="Month",
    yaxis_title="Revenue"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# LOCATION ANALYSIS
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.markdown(
        '<div class="section-title">📍 Location Performance</div>',
        unsafe_allow_html=True
    )

    location_sales = (
        filtered_df
        .groupby("Location", as_index=False)["Total Spent"]
        .sum()
    )

    fig = px.bar(
        location_sales,
        x="Location",
        y="Total Spent",
        text_auto=".2s",
        title="Revenue by Location"
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with col2:

    st.markdown(
        '<div class="section-title">📦 Quantity by Item</div>',
        unsafe_allow_html=True
    )

    quantity_data = (
        filtered_df
        .groupby("Item", as_index=False)["Quantity"]
        .sum()
        .sort_values("Quantity", ascending=False)
    )

    fig = px.bar(
        quantity_data,
        x="Item",
        y="Quantity",
        text_auto=True,
        title="Items Sold"
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TOP SELLING ITEMS
# ============================================================

st.markdown(
    '<div class="section-title">🏆 Top Selling Items</div>',
    unsafe_allow_html=True
)

top_items = (
    filtered_df
    .groupby("Item")
    .agg(
        Quantity=("Quantity", "sum"),
        Revenue=("Total Spent", "sum"),
        Transactions=("Transaction ID", "nunique")
    )
    .sort_values("Revenue", ascending=False)
    .reset_index()
)

top_items["Revenue"] = top_items["Revenue"].round(2)

st.dataframe(
    top_items,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# RAW DATA
# ============================================================

with st.expander("🔎 View Filtered Transaction Data"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <center>
    <small>☕ Cafe Sales Analytics Dashboard | Built with Python + Streamlit + Plotly</small>
    </center>
    """,
    unsafe_allow_html=True
)
