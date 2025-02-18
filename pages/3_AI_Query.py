import streamlit as st
import pickle
import pandas as pd
from datetime import datetime
import re
    
# Page config...
st.set_page_config(page_title="AI Query Analytics", layout="wide")

# Load saved data
try:
    with open('data/dashboard_data.pkl', 'rb') as f:
        data = pickle.load(f)
        df = data['original_df']
except:
    st.error("Error loading data. Please ensure the main dashboard has been run first.")
    st.stop()

# Page Header
st.title("🤖 AI-Powered Data Query")
st.markdown("Ask questions about your maize distribution data")
st.markdown("---")

# Demo explained
st.info("""
🎯 **Demo Mode Active**
This demo supports various questions about:
- Revenue (total, monthly, yearly)
- Volume (total quantity, monthly, yearly)
- Customer information (all customers, categories, regions)
- Performance metrics (top customers, regions)

Try the example queries below or type your own question!
""")

def parse_month(month_str):
    month_map = {
        'jan': 1, 'january': 1,
        'feb': 2, 'february': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'september': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }
    return month_map.get(month_str.lower())

# Enhanced query handlers
def handle_total_revenue(query):
    if re.search(r'(what|how much|show|tell).*total revenue', query.lower()):
        total = df['revenue'].sum()
        return f"💰 Total Revenue: ${total:,.2f}"

def handle_total_quantity(query):
    if re.search(r'(what|how much|show|tell).*total.*quantity|total.*tons', query.lower()):
        total = df['quantity_tons'].sum()
        return f"⚖️ Total Quantity: {total:,.2f} tons"

def handle_revenue_query(query):
    # Pattern for "revenue for [month] [year]"
    pattern = r'revenue.*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* *(20\d\d)' # Very simple yet complicated looking regex.
    match = re.search(pattern, query.lower())
    
    if match:
        month_str = match.group(1)
        year = int(match.group(2))
        month = parse_month(month_str)
        
        if month and year:
            revenue = df[
                (df['date'].dt.year == year) & 
                (df['date'].dt.month == month)
            ]['revenue'].sum()
            
            return f"📊 Revenue for {month_str.capitalize()} {year}: ${revenue:,.2f}"
    
    # Pattern for "revenue in [year]"
    year_pattern = r'revenue.*(20\d\d)'
    year_match = re.search(year_pattern, query.lower())
    
    if year_match:
        year = int(year_match.group(1))
        revenue = df[df['date'].dt.year == year]['revenue'].sum()
        return f"📊 Revenue for {year}: ${revenue:,.2f}"

def handle_quantity_period_query(query):
    # Pattern for "quantity for [month] [year]"
    pattern = r'quantity.*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* *(20\d\d)'
    match = re.search(pattern, query.lower())
    
    if match:
        month_str = match.group(1)
        year = int(match.group(2))
        month = parse_month(month_str)
        
        if month and year:
            quantity = df[
                (df['date'].dt.year == year) & 
                (df['date'].dt.month == month)
            ]['quantity_tons'].sum()
            
            return f"⚖️ Quantity for {month_str.capitalize()} {year}: {quantity:,.2f} tons"
    
    # Pattern for "quantity in [year]"
    year_pattern = r'quantity.*(20\d\d)'
    year_match = re.search(year_pattern, query.lower())
    
    if year_match:
        year = int(year_match.group(1))
        quantity = df[df['date'].dt.year == year]['quantity_tons'].sum()
        return f"⚖️ Quantity for {year}: {quantity:,.2f} tons"

def handle_list_query(query):
    if re.search(r'(what|show|list|tell).*all.*customer', query.lower()):
        customers = sorted(df['customer_name'].unique())
        return f"👥 All Customers ({len(customers)}):\n" + "\n".join([f"- {c}" for c in customers])
    
    if re.search(r'(what|show|list|tell).*all.*categor', query.lower()):
        categories = sorted(df['customer_category'].unique())
        return f"📑 All Categories:\n" + "\n".join([f"- {c}" for c in categories])
    
    if re.search(r'(what|show|list|tell).*all.*region', query.lower()):
        regions = sorted(df['region'].unique())
        return f"🌍 All Regions:\n" + "\n".join([f"- {c}" for c in regions])

def handle_customer_query(query):
    pattern = r'top customer.*(20\d\d)'
    match = re.search(pattern, query.lower())
    
    if match:
        year = int(match.group(1))
        yearly_data = df[df['date'].dt.year == year]
        top_customer = yearly_data.groupby('customer_name')['revenue'].sum().sort_values(ascending=False).head(1)
        
        if not top_customer.empty:
            customer_name = top_customer.index[0]
            revenue = top_customer.values[0]
            return f"🏆 Top customer in {year}: {customer_name} (${revenue:,.2f})"

def handle_region_query(query):
    pattern = r'region.*highest.*sales.*(20\d\d)'
    match = re.search(pattern, query.lower())
    
    if match:
        year = int(match.group(1))
        yearly_data = df[df['date'].dt.year == year]
        top_region = yearly_data.groupby('region')['revenue'].sum().sort_values(ascending=False).head(1)
        
        if not top_region.empty:
            region_name = top_region.index[0]
            revenue = top_region.values[0]
            return f"🌍 Top performing region in {year}: {region_name} (${revenue:,.2f})"

# Initialize session state for the query
if 'query' not in st.session_state:
    st.session_state.query = ""

# Function to update query
def update_query(new_query):
    st.session_state.query = new_query

# Query input using session state
query = st.text_input("Ask your question:", 
                     value=st.session_state.query,
                     placeholder="e.g., What was the revenue for Mar 2024?")

if query:
    # Try each query handler
    handlers = [
        handle_total_revenue,
        handle_total_quantity,
        handle_revenue_query,
        handle_quantity_period_query,
        handle_list_query,
        handle_customer_query,
        handle_region_query
    ]
    
    response = None
    for handler in handlers:
        response = handler(query)
        if response:
            break
    
    if response:
        st.success(response)
    else:
        st.warning("""
        I couldn't understand that question. In this demo, I can answer questions about:
        - Total revenue and quantity
        - Monthly/yearly revenue and quantity
        - Customer lists and categories
        - Regional performance
        - Top customers
        
        Try using one of the example queries below!
        """)

# Add example queries that users can click
st.markdown("---")
st.markdown("### Try these example queries:")

# Example queries in a grid layout
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Revenue Queries**")
    if st.button("💰 What is the total revenue?"):
        update_query("What is the total revenue?")
        st.rerun()
    if st.button("📊 What was the revenue for Mar 2024?"):
        update_query("What was the revenue for Mar 2024?")
        st.rerun()
    if st.button("📈 How much revenue in 2024?"):
        update_query("How much revenue in 2024?")
        st.rerun()

with col2:
    st.markdown("**Volume Queries**")
    if st.button("⚖️ How much total quantity_tons?"):
        update_query("How much total quantity_tons?")
        st.rerun()
    if st.button("📦 How much quantity in Mar 2024?"):
        update_query("How much quantity in Mar 2024?")
        st.rerun()
    if st.button("📊 How much quantity in 2024?"):
        update_query("How much quantity in 2024?")
        st.rerun()

with col3:
    st.markdown("**Information Queries**")
    if st.button("👥 Show all customers"):
        update_query("What are all customers?")
        st.rerun()
    if st.button("📑 List all categories"):
        update_query("Show all categories")
        st.rerun()
    if st.button("🌍 Show all regions"):
        update_query("What are all regions?")
        st.rerun()

# Add a note about the demo nature
st.sidebar.markdown("---")
st.sidebar.markdown("""
### About This Demo
This is a demonstration of AI-like query capabilities using pattern matching. In a production environment, this would be connected to a real LLM API for more sophisticated natural language understanding.

**Current Capabilities:**
- Total revenue and quantity queries
- Monthly/yearly breakdowns
- Customer and regional analysis
- List-based queries (customers, categories, regions)

**Time Period:**
All queries work with data from 2022-2024
""")