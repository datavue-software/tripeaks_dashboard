import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pickle
import os

# Page configuration
st.set_page_config(
    page_title="Competitor Analysis",
    page_icon="📊",
    layout="wide"
)

# Load data from pickle
try:
    with open('data/dashboard_data.pkl', 'rb') as f:
        data_dict = pickle.load(f)
        main_df = data_dict['original_df']
        main_df_filtered = data_dict['filtered_df']
except FileNotFoundError:
    st.error("Please run the main dashboard first to generate the data.")
    st.stop()

# Generate competitor data
def generate_competitor_data(main_df):
    np.random.seed(42)  # Same seed as main page for consistency
    
    # Define major competitors with their characteristics
    competitors = {
        'MaizeCorp Elite': {
            'base_price': 290,
            'price_strategy': 'Premium',
            'service_quality': 9.2,
            'target_customers': ['Global Grain Corp', 'International Food Trade']
        },
        'GrainGiants Int': {
            'base_price': 275,
            'price_strategy': 'Aggressive',
            'service_quality': 8.5,
            'target_customers': ['Maritime Traders Inc', 'Export Trading Group']
        },
        'AgriGlobal Pro': {
            'base_price': 285,
            'price_strategy': 'Balanced',
            'service_quality': 8.8,
            'target_customers': ['World Food Network', 'Continental Supplies']
        },
        'FarmFresh Hub': {
            'base_price': 270,
            'price_strategy': 'Economy',
            'service_quality': 8.0,
            'target_customers': ['Local Grain Exchange', 'Urban Bulk Supplies']
        },
        'EcoGrain Plus': {
            'base_price': 295,
            'price_strategy': 'Organic Focus',
            'service_quality': 9.0,
            'target_customers': ['Digital Food Exchange', 'E-Commerce Foods']
        }
    }
    
    # Create date range matching main data
    dates = pd.date_range(start=main_df['date'].min(), end=main_df['date'].max(), freq='M')
    
    # Define customer movement events
    customer_movements = {
        'Global Grain Corp': {
            'new_supplier': 'MaizeCorp Elite',
            'date': '2024-01-15',
            'reason': 'Price advantage: 15% lower with bulk commitment',
            'impact': 'High',
            'annual_value': '$2.5M'
        },
        'International Food Trade': {
            'new_supplier': 'GrainGiants Int',
            'date': '2023-09-01',
            'reason': 'Aggressive pricing and flexible payment terms',
            'impact': 'Medium',
            'annual_value': '$1.8M'
        },
        'Maritime Traders Inc': {
            'new_supplier': 'AgriGlobal Pro',
            'date': '2024-02-01',
            'reason': 'Integrated logistics solution',
            'impact': 'Medium',
            'annual_value': '$1.2M'
        },
        'Export Trading Group': {
            'new_supplier': 'FarmFresh Hub',
            'date': '2023-11-15',
            'reason': 'Regional warehouse access and lower prices',
            'impact': 'High',
            'annual_value': '$2.1M'
        }
    }

    data = []
    # Generate monthly data for each competitor
    for date in dates:
        for comp_name, comp_info in competitors.items():
            base_price = comp_info['base_price']
            
            # Add seasonal variation
            month_factor = 1 + 0.1 * np.sin(date.month * np.pi / 6)
            
            # Add strategic price changes
            if comp_name in ['MaizeCorp Elite', 'GrainGiants Int'] and date >= pd.Timestamp('2023-09-01'):
                base_price *= 0.85  # 15% reduction for aggressive competitors
            
            # Calculate metrics
            price = base_price * month_factor * (1 + 0.02 * np.random.randn())
            market_share = np.random.normal(20, 2)
            service_score = comp_info['service_quality'] + np.random.normal(0, 0.1)
            
            data.append({
                'date': date,
                'competitor': comp_name,
                'price_per_ton': price,
                'market_share': market_share,
                'service_quality': service_score,
                'price_strategy': comp_info['price_strategy']
            })
    
    df = pd.DataFrame(data)
    
    # Add customer movement annotations
    df['events'] = ''
    for customer, movement in customer_movements.items():
        mask = (df['date'] == pd.Timestamp(movement['date'])) & \
               (df['competitor'] == movement['new_supplier'])
        df.loc[mask, 'events'] = f"Gained {customer}: {movement['reason']}"
    
    return df, customer_movements, competitors

# Generate data
df_competitor, customer_movements, competitors_info = generate_competitor_data(main_df)

# Dashboard header
st.title("📊 Competitor Analysis")
st.markdown("### Market Intelligence Dashboard")
st.markdown("---")

# Filters in sidebar
st.sidebar.title("Filters")

# Clear All Filters button
if st.sidebar.button("Clear All Filters"):
    st.rerun()

# Date filters with two columns
filter_col1, filter_col2 = st.sidebar.columns(2)

with filter_col1:
    year_options = sorted(df_competitor['date'].dt.year.unique())
    selected_years = st.multiselect('Select Years', year_options,
                                  default=year_options[-1:])

with filter_col2:
    month_options = list(range(1, 13))
    month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 
                  7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    month_options_named = [month_names[m] for m in month_options]
    selected_month = st.selectbox('Select Month', ['All'] + month_options_named)

# Filter data
mask = df_competitor['date'].dt.year.isin(selected_years)
if selected_month != 'All':
    selected_month_num = list(month_names.keys())[list(month_names.values()).index(selected_month)]
    mask = mask & (df_competitor['date'].dt.month == selected_month_num)
df_filtered = df_competitor[mask]

# Key Metrics
st.subheader("Market Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_market_price = df_filtered['price_per_ton'].mean()
    st.metric("Average Market Price", f"${avg_market_price:.2f}")

with col2:
    price_volatility = df_filtered['price_per_ton'].std()
    st.metric("Price Volatility", f"${price_volatility:.2f}")

with col3:
    lost_customers = len(customer_movements)
    st.metric("Lost Major Customers", str(lost_customers))

with col4:
    total_lost_value = sum([float(m['annual_value'].replace('$','').replace('M','')) 
                           for m in customer_movements.values()])
    st.metric("Est. Annual Revenue Loss", f"${total_lost_value:.1f}M")

# Main visualizations
st.markdown("---")

# Price Trends with Customer Movement Annotations
st.subheader("Competitor Price Trends and Customer Movements")
fig_price = px.line(df_competitor, x='date', y='price_per_ton', color='competitor',
                    title='Price Evolution with Customer Movements')

# Add annotations for customer movements
for customer, movement in customer_movements.items():
    fig_price.add_annotation(
        x=movement['date'],
        y=df_competitor[df_competitor['competitor'] == movement['new_supplier']]['price_per_ton'].mean(),
        text=f"{customer} → {movement['new_supplier']}",
        showarrow=True,
        arrowhead=1,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="#636363"
    )

st.plotly_chart(fig_price, use_container_width=True)

# Create two columns for additional charts
col1, col2 = st.columns(2)

with col1:
    # Market Share Analysis
    st.subheader("Market Share Distribution")
    fig_share = px.pie(df_filtered.groupby('competitor')['market_share'].mean().reset_index(),
                       values='market_share', names='competitor',
                       title='Current Market Share Distribution')
    st.plotly_chart(fig_share, use_container_width=True)

    # Competitor Price Comparison
    st.subheader("Price Positioning")
    fig_price_comp = px.box(df_filtered, x='competitor', y='price_per_ton',
                           title='Price Distribution by Competitor')
    st.plotly_chart(fig_price_comp, use_container_width=True)

with col2:
    # Service Quality Comparison
    st.subheader("Service Quality Comparison")
    fig_quality = px.bar(df_filtered.groupby('competitor')['service_quality'].mean().reset_index(),
                        x='competitor', y='service_quality',
                        title='Service Quality Score by Competitor')
    fig_quality.update_layout(yaxis_range=[7, 10])
    st.plotly_chart(fig_quality, use_container_width=True)

    # Price Strategy Analysis
    st.subheader("Pricing Strategies")
    strategy_df = pd.DataFrame([(k, v['price_strategy']) 
                              for k, v in competitors_info.items()], 
                              columns=['Competitor', 'Strategy'])
    fig_strategy = go.Figure(data=[go.Table(
        header=dict(values=['Competitor', 'Pricing Strategy'],
                   fill_color='paleturquoise',
                   align='left'),
        cells=dict(values=[strategy_df['Competitor'], strategy_df['Strategy']],
                  fill_color='lavender',
                  align='left'))
    ])
    st.plotly_chart(fig_strategy, use_container_width=True)

# Customer Movement Analysis
st.markdown("---")
st.subheader("Lost Customer Analysis")

# Create a table of customer movements
movement_data = []
for customer, info in customer_movements.items():
    movement_data.append({
        'Customer': customer,
        'New Supplier': info['new_supplier'],
        'Movement Date': info['date'],
        'Primary Reason': info['reason'],
        'Business Impact': info['impact'],
        'Annual Value Lost': info['annual_value']
    })

movement_df = pd.DataFrame(movement_data)
st.dataframe(movement_df, use_container_width=True)

# Key Insights
st.markdown("### Key Insights")
st.markdown("""
- **Pricing Pressure**: Competitors offering 15% lower prices have successfully attracted key customers
- **Revenue Impact**: Total estimated annual revenue loss of ${:.1f}M from customer movements
- **Timing Pattern**: Major customer losses concentrated in Q4 2023 and Q1 2024
- **Competition Strategy**: Two major competitors (MaizeCorp Elite and GrainGiants Int) implementing aggressive pricing strategies
""".format(total_lost_value))

# Add a note about the data
st.sidebar.markdown("---")
st.sidebar.markdown("ℹ️ **Note:** Competitor data is based on market analysis and estimates.")