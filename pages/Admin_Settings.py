import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import os
import uuid

# Page configuration
st.set_page_config(page_title="Admin Settings", layout="wide")

# Initialize session state for admin data
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

if 'users' not in st.session_state:
    st.session_state.users = [
        {"id": "1", "name": "Admin User", "email": "admin@example.com", "role": "Admin", "last_login": "2024-04-21"},
        {"id": "2", "name": "John Analyst", "email": "john@example.com", "role": "Analyst", "last_login": "2024-04-22"},
        {"id": "3", "name": "Sarah Manager", "email": "sarah@example.com", "role": "Manager", "last_login": "2024-04-20"}
    ]

if 'invoices' not in st.session_state:
    st.session_state.invoices = [
        {"id": "INV-2024-001", "date": "2024-01-15", "amount": 1500.00, "status": "Paid", "description": "Dashboard Setup"},
        {"id": "INV-2024-002", "date": "2024-02-15", "amount": 500.00, "status": "Paid", "description": "Monthly Maintenance"},
        {"id": "INV-2024-003", "date": "2024-03-15", "amount": 750.00, "status": "Pending", "description": "Feature Additions"},
        {"id": "INV-2024-004", "date": "2024-04-15", "amount": 500.00, "status": "Pending", "description": "Monthly Maintenance"}
    ]

# Authentication function
def authenticate(password):
    # In a real app, use a secure password validation method
    return password == "admin123"  # Demo password

# Page header with styling
st.markdown("""
<style>
    .admin-header {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .admin-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .status-pill {
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .status-paid {
        background-color: #d1f7c4;
        color: #2e7d32;
    }
    .status-pending {
        background-color: #ffecb3;
        color: #ff6f00;
    }
</style>
<div class="admin-header">
    <h1>⚙️ Admin Settings</h1>
    <p>Manage your dashboard settings, users, and billing information</p>
</div>
""", unsafe_allow_html=True)

# Authentication
if not st.session_state.admin_authenticated:
    st.markdown('<div class="admin-section">', unsafe_allow_html=True)
    st.subheader("🔒 Admin Authentication")
    password = st.text_input("Enter admin password:", type="password")
    if st.button("Login"):
        if authenticate(password):
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Invalid password. Please try again.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show demo credentials for the demo
    st.info("👨‍💻 **Demo credentials:** Password is 'admin123'")
else:
    # Admin dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "👥 User Management", "💰 Billing", "⚙️ Settings"])
    
    with tab1:
        st.markdown('<div class="admin-section">', unsafe_allow_html=True)
        st.subheader("Dashboard Overview")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Active Users", "3", "+1")
        with col2:
            st.metric("Data Freshness", "2 days ago", "-1 day")
        with col3:
            st.metric("API Quota Used", "67%", "+12%")
        
        st.subheader("System Status")
        st.success("All systems operational")
        
        # Last update info
        st.info(f"Last data refresh: {(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')}")
        
        # Schedule next refresh
        st.subheader("Schedule Data Refresh")
        refresh_date = st.date_input("Next scheduled refresh:", 
                                     datetime.now() + timedelta(days=7))
        if st.button("Update Schedule"):
            st.success(f"Data refresh scheduled for {refresh_date}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="admin-section">', unsafe_allow_html=True)
        st.subheader("User Management")
        
        # Display current users
        st.write("Current Users:")
        users_df = pd.DataFrame(st.session_state.users)
        st.dataframe(users_df, use_container_width=True)
        
        # Add new user form
        st.subheader("Add New User")
        with st.form("new_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Name")
                new_email = st.text_input("Email")
            with col2:
                new_role = st.selectbox("Role", ["Viewer", "Analyst", "Manager", "Admin"])
                new_password = st.text_input("Temporary Password", type="password")
            
            submit_button = st.form_submit_button("Add User")
            if submit_button:
                if new_name and new_email and new_password:
                    new_user = {
                        "id": str(uuid.uuid4())[:8],
                        "name": new_name,
                        "email": new_email,
                        "role": new_role,
                        "last_login": "Never"
                    }
                    st.session_state.users.append(new_user)
                    st.success(f"User {new_name} added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all fields")
        
        # User permissions explanation
        st.subheader("Permission Levels")
        permissions = {
            "Viewer": "Can view dashboards only",
            "Analyst": "Can view and export data",
            "Manager": "Can view, export, and edit visualizations",
            "Admin": "Full access to all features and settings"
        }
        
        for role, description in permissions.items():
            st.markdown(f"**{role}**: {description}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="admin-section">', unsafe_allow_html=True)
        st.subheader("Billing Information")
        
        # Display current subscription
        st.write("**Current Plan:** Premium Analytics")
        st.write("**Renewal Date:** May 15, 2024")
        st.write("**Monthly Cost:** $500")
        
        # Display invoices
        st.subheader("Invoices")
        
        # Create a formatted invoice display
        for inv in st.session_state.invoices:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{inv['id']}** - {inv['description']}")
                st.write(f"Date: {inv['date']}")
            with col2:
                st.write(f"**${inv['amount']:.2f}**")
            with col3:
                status_class = "status-paid" if inv['status'] == "Paid" else "status-pending"
                st.markdown(f"<div class='status-pill {status_class}'>{inv['status']}</div>", 
                           unsafe_allow_html=True)
            st.markdown("---")
        
        # Add payment method form
        st.subheader("Add Payment Method")
        with st.form("payment_form"):
            col1, col2 = st.columns(2)
            with col1:
                card_name = st.text_input("Name on Card")
                card_number = st.text_input("Card Number")
            with col2:
                expiry = st.text_input("Expiry (MM/YY)")
                cvv = st.text_input("CVV", max_chars=4)
            
            submit_button = st.form_submit_button("Add Payment Method")
            if submit_button:
                st.success("Payment method added successfully!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="admin-section">', unsafe_allow_html=True)
        st.subheader("General Settings")
        
        # Color theme
        theme = st.selectbox("Dashboard Theme", ["Light", "Dark", "System Default"])
        
        # Notification settings
        st.subheader("Notifications")
        email_reports = st.checkbox("Send weekly email reports", value=True)
        alert_threshold = st.slider("Alert Threshold (%)", 0, 100, 20)
        
        # Data retention policy
        st.subheader("Data Retention")
        retention_period = st.selectbox("Data Retention Period", 
                                      ["3 Months", "6 Months", "1 Year", "2 Years", "Forever"])
        
        # Save settings button
        if st.button("Save Settings"):
            st.success("Settings saved successfully!")
            
        # Danger zone
        st.subheader("Danger Zone")
        st.warning("The following actions cannot be undone!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset Dashboard"):
                st.error("Dashboard has been reset to default settings")
        with col2:
            if st.button("Clear All Data"):
                st.error("This functionality is disabled in demo mode")
        st.markdown('</div>', unsafe_allow_html=True)
        
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()