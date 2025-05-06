import streamlit as st
import os
import json
import uuid
from pathlib import Path
import pandas as pd  # Add explicit pandas import

# Page configuration
st.set_page_config(page_title="Plugin Marketplace", layout="wide")

# Initialize session state for current time if needed
if "current_time" not in st.session_state:
    st.session_state["current_time"] = "2024-05-06"

# Initialize plugin directory - with error handling
try:
    PLUGIN_DIR = Path("plugins")
    PLUGIN_DIR.mkdir(exist_ok=True)
    
    PLUGIN_CONFIG_FILE = PLUGIN_DIR / "plugin_config.json"
    
    # Initialize plugin configuration
    if not PLUGIN_CONFIG_FILE.exists():
        initial_config = {
            "installed_plugins": {},
            "active_plugins": []
        }
        with open(PLUGIN_CONFIG_FILE, 'w') as f:
            json.dump(initial_config, f)
    
    # Load plugin configuration
    with open(PLUGIN_CONFIG_FILE, 'r') as f:
        plugin_config = json.load(f)
except Exception as e:
    # Graceful fallback if file operations fail
    st.error(f"Error initializing plugin system: {str(e)}")
    st.info("Using temporary plugin configuration for demo purposes.")
    plugin_config = {
        "installed_plugins": {},
        "active_plugins": []
    }

# Page Header
st.title("🧩 Plugin Marketplace")
st.markdown("Extend your dashboard with powerful plugins")
st.markdown("---")

# Available plugins (in a real system, this could be fetched from a server)
AVAILABLE_PLUGINS = [
    {
        "id": "export_excel",
        "name": "Advanced Excel Export",
        "description": "Export any dashboard view to formatted Excel files with charts",
        "version": "1.0.0",
        "author": "Maize Analytics Team",
        "icon": "📊",
        "category": "Export",
    },
    {
        "id": "predictive_analysis",
        "name": "Predictive Sales Analysis",
        "description": "ML-powered sales forecasting based on historical data",
        "version": "1.2.1",
        "author": "Maize Analytics Team",
        "icon": "🔮",
        "category": "Analysis",
    },
    {
        "id": "competitor_tracker",
        "name": "Competitor Price Tracker",
        "description": "Monitor and compare competitor pricing in real-time",
        "version": "0.9.5",
        "author": "Market Intelligence Inc.",
        "icon": "👁️",
        "category": "Market Intelligence",
    },
    {
        "id": "custom_notifications",
        "name": "Custom Notifications",
        "description": "Set up custom alerts based on data thresholds",
        "version": "1.1.0",
        "author": "Maize Analytics Team",
        "icon": "🔔",
        "category": "Notifications",
    },
    {
        "id": "pdf_reports",
        "name": "PDF Report Generator",
        "description": "Create beautiful PDF reports from dashboard data",
        "version": "1.3.2",
        "author": "ReportCraft Solutions",
        "icon": "📄",
        "category": "Export",
    },
    {
        "id": "weather_data",
        "name": "Weather Data Integration",
        "description": "Correlate sales with weather patterns across regions",
        "version": "1.0.3",
        "author": "Climate Analytics",
        "icon": "🌦️",
        "category": "Data Integration",
    }
]

# Create tabs for marketplace and management
tab1, tab2, tab3 = st.tabs(["🏪 Marketplace", "⚙️ Manage Plugins", "🔌 Upload Custom Plugin"])

with tab1:
    st.subheader("Available Plugins")
    
    # Filter by category
    categories = sorted(list(set(plugin["category"] for plugin in AVAILABLE_PLUGINS)))
    selected_category = st.selectbox("Filter by category", ["All"] + categories)
    
    # Search
    search_query = st.text_input("Search plugins", "")
    
    # Filter plugins
    filtered_plugins = AVAILABLE_PLUGINS
    if selected_category != "All":
        filtered_plugins = [p for p in filtered_plugins if p["category"] == selected_category]
    
    if search_query:
        filtered_plugins = [p for p in filtered_plugins 
                           if search_query.lower() in p["name"].lower() 
                           or search_query.lower() in p["description"].lower()]
    
    # Display plugins in a grid
    if not filtered_plugins:
        st.info("No plugins match your filters.")
    else:
        # Create a 3-column grid for plugins
        cols = st.columns(3)
        
        for i, plugin in enumerate(filtered_plugins):
            col_idx = i % 3
            
            with cols[col_idx]:
                plugin_id = plugin["id"]
                is_installed = plugin_id in plugin_config["installed_plugins"]
                is_active = plugin_id in plugin_config["active_plugins"]
                
                st.markdown(f"""
                <div style="
                    border: 1px solid #ddd; 
                    border-radius: 10px; 
                    padding: 15px; 
                    margin-bottom: 20px;
                    background-color: {'#f8f9fa' if not is_active else '#e6f7ff'};
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <div style="font-size: 24px; margin-right: 10px;">{plugin["icon"]}</div>
                        <div>
                            <h3 style="margin: 0;">{plugin["name"]}</h3>
                            <p style="margin: 0; color: #666; font-size: 0.8em;">v{plugin["version"]} by {plugin["author"]}</p>
                        </div>
                    </div>
                    <p>{plugin["description"]}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="
                            background-color: #eee; 
                            padding: 2px 8px; 
                            border-radius: 10px; 
                            font-size: 0.8em;
                        ">{plugin["category"]}</span>
                        <div>
                            {'✅ Active' if is_active else ('⚪ Installed' if is_installed else '')}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Plugin actions
                if is_installed:
                    if is_active:
                        if st.button(f"Deactivate {plugin['name']}", key=f"deactivate_{plugin_id}"):
                            plugin_config["active_plugins"].remove(plugin_id)
                            try:
                                with open(PLUGIN_CONFIG_FILE, 'w') as f:
                                    json.dump(plugin_config, f)
                            except Exception as e:
                                st.warning(f"Could not save configuration: {str(e)}")
                            st.rerun()
                    else:
                        if st.button(f"Activate {plugin['name']}", key=f"activate_{plugin_id}"):
                            plugin_config["active_plugins"].append(plugin_id)
                            try:
                                with open(PLUGIN_CONFIG_FILE, 'w') as f:
                                    json.dump(plugin_config, f)
                            except Exception as e:
                                st.warning(f"Could not save configuration: {str(e)}")
                            st.rerun()
                    
                    if st.button(f"Uninstall {plugin['name']}", key=f"uninstall_{plugin_id}"):
                        if plugin_id in plugin_config["active_plugins"]:
                            plugin_config["active_plugins"].remove(plugin_id)
                        del plugin_config["installed_plugins"][plugin_id]
                        try:
                            with open(PLUGIN_CONFIG_FILE, 'w') as f:
                                json.dump(plugin_config, f)
                        except Exception as e:
                            st.warning(f"Could not save configuration: {str(e)}")
                        st.rerun()
                else:
                    if st.button(f"Install {plugin['name']}", key=f"install_{plugin_id}"):
                        plugin_config["installed_plugins"][plugin_id] = {
                            "version": plugin["version"],
                            "installed_at": st.session_state.get("current_time", "2024-05-06"),
                        }
                        try:
                            with open(PLUGIN_CONFIG_FILE, 'w') as f:
                                json.dump(plugin_config, f)
                        except Exception as e:
                            st.warning(f"Could not save configuration: {str(e)}")
                        st.success(f"Installed {plugin['name']}!")
                        st.rerun()

with tab2:
    st.subheader("Manage Installed Plugins")
    
    installed_plugins = plugin_config["installed_plugins"]
    
    if not installed_plugins:
        st.info("No plugins are currently installed. Visit the Marketplace tab to install plugins.")
    else:
        st.write(f"You have {len(installed_plugins)} installed plugins.")
        
        # Create a table of installed plugins
        plugin_data = []
        for plugin_id, plugin_info in installed_plugins.items():
            plugin_data.append({
                "ID": plugin_id,
                "Name": next((p["name"] for p in AVAILABLE_PLUGINS if p["id"] == plugin_id), plugin_id),
                "Version": plugin_info["version"],
                "Status": "Active" if plugin_id in plugin_config["active_plugins"] else "Inactive",
                "Installed On": plugin_info.get("installed_at", "Unknown")
            })
        
        plugin_df = pd.DataFrame(plugin_data)
        st.dataframe(plugin_df, use_container_width=True)
        
        # Bulk actions
        st.subheader("Bulk Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Activate All"):
                plugin_config["active_plugins"] = list(installed_plugins.keys())
                try:
                    with open(PLUGIN_CONFIG_FILE, 'w') as f:
                        json.dump(plugin_config, f)
                except Exception as e:
                    st.warning(f"Could not save configuration: {str(e)}")
                st.success("Activated all plugins!")
                st.rerun()
        
        with col2:
            if st.button("Deactivate All"):
                plugin_config["active_plugins"] = []
                try:
                    with open(PLUGIN_CONFIG_FILE, 'w') as f:
                        json.dump(plugin_config, f)
                except Exception as e:
                    st.warning(f"Could not save configuration: {str(e)}")
                st.success("Deactivated all plugins!")
                st.rerun()

with tab3:
    st.subheader("Upload Custom Plugin")
    
    st.markdown("""
    Custom plugins allow you to extend the dashboard with your own functionality.
    
    **Plugin Requirements:**
    - A Python file (.py) with a class that implements the Plugin interface
    - No malicious or unsafe code
    - Follows our plugin development guidelines
    
    **Plugin Capabilities:**
    - Add new visualizations
    - Connect to external data sources
    - Add custom exports
    - Extend the dashboard UI
    """)
    
    uploaded_file = st.file_uploader("Upload Python Plugin (.py file)", type=["py"])
    
    plugin_name = st.text_input("Plugin Name", "")
    plugin_description = st.text_area("Plugin Description", "")
    plugin_category = st.selectbox("Plugin Category", categories if categories else ["Analysis", "Export", "Visualization"])
    
    if uploaded_file and plugin_name and plugin_description and plugin_category:
        if st.button("Submit Plugin"):
            # In a real system, you would:
            # 1. Validate the plugin code for security
            # 2. Save it to the plugins directory
            # 3. Register it in the plugin system
            
            plugin_id = f"custom_{uuid.uuid4().hex[:8]}"
            
            # For demo purposes, just pretend we've installed it
            plugin_config["installed_plugins"][plugin_id] = {
                "version": "1.0.0",
                "installed_at": st.session_state.get("current_time", "2024-05-06"),
                "custom": True,
                "name": plugin_name,
                "description": plugin_description,
                "category": plugin_category
            }
            
            try:
                with open(PLUGIN_CONFIG_FILE, 'w') as f:
                    json.dump(plugin_config, f)
            except Exception as e:
                st.warning(f"Could not save configuration: {str(e)}")
                
            st.success(f"Plugin '{plugin_name}' uploaded and installed successfully!")
            st.info("Note: In a production environment, custom plugins would undergo security review before installation.")
    else:
        st.info("Please fill in all fields to upload a custom plugin.")

# Documentation section
st.markdown("---")
st.subheader("📚 Plugin Development Guide")
st.markdown("""
Want to create your own plugins? Check out our developer documentation to learn how to build
custom plugins that integrate with our dashboard.

Plugins can be developed using Python and should implement our plugin interface:

```python
class ExamplePlugin:
    def __init__(self):
        self.name = "Example Plugin"
        self.version = "1.0.0"
        
    def run(self, dashboard_data):
        # Plugin logic here
        pass
        
    def get_ui(self):
        # Return a Streamlit UI component
        return st.container()
```

**Resources:**
- [Plugin Development Documentation](#)
- [Plugin API Reference](#)
- [Example Plugins Repository](#)
""")

# Add a note about the demo nature
st.sidebar.markdown("---")
st.sidebar.info("""
**About Plugins**

Plugins extend your dashboard with new capabilities without requiring code changes.

Currently installed: {} plugins
Active: {} plugins
""".format(len(plugin_config["installed_plugins"]), len(plugin_config["active_plugins"])))