import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pickle
import os

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Page configuration
st.set_page_config(page_title="Maize Distribution Analytics", layout="wide")

# Create customer data
def generate_customer_base():
    local_customers = [
        "Metro Wholesale Ltd", "City Bulk Foods", "Region Foods Co", 
        "Prime Distributors", "Local Grain Exchange", "Urban Bulk Supplies",
        "District Foods Inc", "Central Wholesale Co", "Town Grain Traders",
        "Municipal Food Supply", "Community Bulk Store", "Local Mart Chain",
        "City Food Network", "Regional Bulk Foods", "Metro Food Alliance"
    ]
    
    international_customers = [
        "Global Grain Corp", "International Food Trade", "World Maize Exchange",
        "Continental Supplies", "Ocean Foods International", "Cross Border Trading",
        "Global Bulk Foods", "International Wholesale Co", "World Food Network",
        "Maritime Traders Inc", "Export Trading Group", "Global Food Alliance",
        "International Grain Co", "Overseas Food Supply", "World Trade Foods"
    ]
    
    online_customers = [
        "E-Grain Trading", "Digital Food Exchange", "Online Bulk Foods",
        "Virtual Trading Co", "E-Commerce Foods", "Digital Wholesale Network",
        "Cloud Trading Group", "Online Mart Supply", "Digital Food Alliance",
        "E-Bulk Solutions", "Virtual Food Trade", "Online Exchange Co",
        "Digital Grain Store", "E-Commerce Trades", "Web Food Network"
    ]
    
    customers_data = []
    for customer in local_customers:
        customers_data.append({"name": customer, "category": "Local"})
    for customer in international_customers:
        customers_data.append({"name": customer, "category": "International"})
    for customer in online_customers:
        customers_data.append({"name": customer, "category": "Online"})
    
    return pd.DataFrame(customers_data)

# Generate dummy data
def generate_dummy_data(n_records=5000):
    np.random.seed(42)
    
    # Generate customer base
    customers_df = generate_customer_base()
    
    # Date range for last 3 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1095)
    dates = pd.date_range(start=start_date, end=end_date, periods=n_records)
    
    # Create dummy data
    data = {
        'date': dates,
        'product_type': np.random.choice(['White Maize', 'Yellow Maize', 'Organic Maize'], n_records),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_records),
        'quantity_tons': np.random.normal(100, 20, n_records),
        'price_per_ton': np.random.normal(300, 50, n_records),
    }
    
    # Randomly assign customers and their categories
    customer_indices = np.random.choice(len(customers_df), n_records)
    data['customer_name'] = customers_df.iloc[customer_indices]['name'].values
    data['customer_category'] = customers_df.iloc[customer_indices]['category'].values
    
    df = pd.DataFrame(data)
    
    # Calculate revenue
    df['revenue'] = df['quantity_tons'] * df['price_per_ton']
    
    # Add yearly growth trend (5% year over year)
    df['years_from_start'] = (df['date'] - df['date'].min()).dt.days / 365
    df['growth_factor'] = 1 + (df['years_from_start'] * 0.05)
    df['revenue'] = df['revenue'] * df['growth_factor']
    
    # Add seasonal patterns
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    seasonal_factor = np.sin(df['month'] * np.pi / 6) * 0.2 + 1
    df['revenue'] = df['revenue'] * seasonal_factor
    
    # Add active/inactive status (90% active, 10% inactive)
    df['status'] = np.random.choice(['Active', 'Inactive'], n_records, p=[0.9, 0.1])
    
    # Simulate a major customer loss scenario
    target_customer = "Global Grain Corp"
    mask = (df['customer_name'] == target_customer) & (df['date'] > (end_date - timedelta(days=180)))
    df.loc[mask, 'revenue'] = df.loc[mask, 'revenue'] * 0.3
    df.loc[mask, 'status'] = 'Inactive'
    
    return df.drop(['years_from_start', 'growth_factor'], axis=1)

# Generate data
df = generate_dummy_data()

# Dashboard header
st.title("🌽 Maize Distribution Analytics")
st.subheader("Basic Insights Dashboard")
st.markdown("---")

# Sidebar filters
st.sidebar.title("Filters")

# Clear All Filters button
if st.sidebar.button("Clear All Filters"):
    st.rerun()

# Date filters with two columns
filter_col1, filter_col2 = st.sidebar.columns(2)

with filter_col1:
    year_options = sorted(df['year'].unique())
    selected_years = st.multiselect('Select Years', year_options, 
                                  default=year_options[-1:],
                                  key='year_filter')

with filter_col2:
    month_options = list(range(1, 13))
    month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 
                  7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    month_options_named = [month_names[m] for m in month_options]
    selected_month = st.selectbox('Select Month', ['All'] + month_options_named)

# Other filters
customer_options = sorted(df['customer_name'].unique())
selected_customers = st.sidebar.multiselect('Select Customers', customer_options, default=[])

category_options = sorted(df['customer_category'].unique())
selected_categories = st.sidebar.selectbox('Select Customer Category', 
                                         ['All'] + list(category_options))

region_options = sorted(df['region'].unique())
selected_region = st.sidebar.selectbox('Select Region', ['All'] + list(region_options))

product_options = sorted(df['product_type'].unique())
selected_product = st.sidebar.selectbox('Select Product', ['All'] + list(product_options))

status_options = sorted(df['status'].unique())
selected_status = st.sidebar.selectbox('Select Status', ['All'] + list(status_options))

# Filter logic
mask = df['year'].isin(selected_years)

if selected_month != 'All':
    selected_month_num = list(month_names.keys())[list(month_names.values()).index(selected_month)]
    mask = mask & (df['month'] == selected_month_num)

if selected_customers:
    mask = mask & df['customer_name'].isin(selected_customers)
if selected_categories != 'All':
    mask = mask & (df['customer_category'] == selected_categories)
if selected_region != 'All':
    mask = mask & (df['region'] == selected_region)
if selected_product != 'All':
    mask = mask & (df['product_type'] == selected_product)
if selected_status != 'All':
    mask = mask & (df['status'] == selected_status)

df_filtered = df[mask]

# Top-level metrics
col1, col2, col3, col4 = st.columns(4)

total_revenue = df_filtered['revenue'].sum()
avg_order_size = df_filtered['quantity_tons'].mean()
total_volume = df_filtered['quantity_tons'].sum()
active_customers = df_filtered[df_filtered['status'] == 'Active']['customer_name'].nunique()

with col1:
    st.metric("Total Revenue", f"${total_revenue:,.0f}")
with col2:
    st.metric("Total Volume (Tons)", f"{total_volume:,.0f}")
with col3:
    st.metric("Avg Order Size (Tons)", f"{avg_order_size:.1f}")
with col4:
    st.metric("Active Customers", active_customers)

# Add spacing after metrics
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# Revenue Trend - Full Width
st.subheader("Revenue Trend")
monthly_revenue = df_filtered.groupby(df_filtered['date'].dt.strftime('%Y-%m'))[['revenue']].sum().reset_index()

# Enhanced line chart with markers and values
fig_revenue = go.Figure()
fig_revenue.add_trace(go.Scatter(
    x=monthly_revenue['date'],
    y=monthly_revenue['revenue'],
    mode='lines+markers+text',
    text=monthly_revenue['revenue'].apply(lambda x: f'${x:,.0f}'),
    textposition='top center',
    textfont=dict(size=8),  # Smaller text size
    line=dict(width=2),
    marker=dict(size=8)
))

fig_revenue.update_layout(
    title='Monthly Revenue Trend',
    xaxis_title='Month',
    yaxis_title='Revenue ($)',
    template='plotly_white',
    height=500,  # Increased height
    margin=dict(t=50, r=50, l=50, b=50),  # Increased margins
)
st.plotly_chart(fig_revenue, use_container_width=True)

# Add spacing after revenue trend
st.markdown("---")

# Create two columns for the first row of charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Regional Performance")
    region_performance = df_filtered.groupby('region')[['revenue']].sum().reset_index()
    fig_region = px.bar(region_performance, x='region', y='revenue',
                       title='Revenue by Region',
                       labels={'region': 'Region', 'revenue': 'Revenue ($)'},
                       template='plotly_white',
                       height=400)
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    st.subheader("Customer Category Distribution")
    category_dist = df_filtered.groupby('customer_category')['revenue'].sum().reset_index()
    fig_category = px.pie(category_dist, values='revenue', names='customer_category',
                         title='Revenue by Customer Category',
                         template='plotly_white',
                         height=400)
    st.plotly_chart(fig_category, use_container_width=True)

# Create two columns for the second row of charts
col3, col4 = st.columns(2)

with col3:
    st.subheader("Product Mix")
    product_mix = df_filtered.groupby('product_type')['quantity_tons'].sum().reset_index()
    fig_product = px.pie(product_mix, values='quantity_tons', names='product_type',
                        title='Sales Volume by Product Type',
                        template='plotly_white',
                        height=400)
    st.plotly_chart(fig_product, use_container_width=True)

# Customer table with filtered data
st.markdown("---")
st.subheader("Full Data Table")

# Create filtered customer table using the same filtered dataset
customer_table = df_filtered.groupby(['customer_name', 'customer_category', 'region', 'status']).\
    agg({
        'revenue': 'sum',
        'quantity_tons': 'sum'
    }).reset_index()

customer_table = customer_table.sort_values('revenue', ascending=False)
customer_table['revenue'] = customer_table['revenue'].round(2)
customer_table['quantity_tons'] = customer_table['quantity_tons'].round(2)

# Format revenue as currency
customer_table['revenue'] = customer_table['revenue'].apply(lambda x: f"${x:,.2f}")

# Rename columns for better presentation
customer_table.columns = ['Customer Name', 'Category', 'Region', 'Status', 'Revenue', 'Volume (Tons)']

st.dataframe(customer_table, use_container_width=True)

# Save the dataframe to pickle for other pages to use
data_to_save = {
    'original_df': df,
    'filtered_df': df_filtered,
    'filter_state': {
        'selected_years': selected_years,
        'selected_month': selected_month,
        'selected_customers': selected_customers,
        'selected_categories': selected_categories,
        'selected_region': selected_region,
        'selected_product': selected_product,
        'selected_status': selected_status
    }
}

with open('data/dashboard_data.pkl', 'wb') as f:
    pickle.dump(data_to_save, f)

# Add a note about the data
st.sidebar.markdown("---")
st.sidebar.markdown("ℹ️ **Note:** This dashboard uses dummy data for demonstration purposes.")