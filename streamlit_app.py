import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os

from config.config import CITIES, TEMPERATURE_UNIT, ALERT_THRESHOLD
from src.data_processing import process_weather_data, calculate_daily_summary
from src.database.db_manager import DatabaseManager
from src.database.db_operations import DatabaseOperations
from src.alerts import AlertSystem
from src.mock_data_generator import generate_mock_weather_data
from src.data_retrieval import fetch_all_cities


class StreamlitWeatherApp:
    def __init__(self):
        # Initialize mode selection state
        if 'use_mock' not in st.session_state:
            st.session_state.use_mock = True

        self.db_manager = None
        self.db_ops = None
        self.alert_system = None

    def initialize_system(self, use_mock):
        """Initialize or reinitialize the system with selected mode"""
        self.db_manager = DatabaseManager(
            'sqlite:///mock_weather_data.db' if use_mock else 'sqlite:///real_weather_data.db',
            'mock' if use_mock else 'real'
        )
        self.db_ops = DatabaseOperations(self.db_manager)
        self.alert_system = AlertSystem()

    def run(self):
        st.set_page_config(
            page_title="Weather Monitoring Dashboard",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Sidebar Configuration
        st.sidebar.title("Weather Dashboard Settings")

        # Data Mode Selection
        st.sidebar.header("Data Source Configuration")

        # Mode selection with radio buttons
        mode = st.sidebar.radio(
            "Select Data Source",
            ["Mock Data", "Real-time Data"],
            index=0 if st.session_state.use_mock else 1,
            help="Choose between mock data for testing or real-time weather data"
        )

        # Update session state based on mode selection
        use_mock = mode == "Mock Data"

        # Check if mode has changed
        if use_mock != st.session_state.use_mock:
            st.session_state.use_mock = use_mock
            # Clear any existing data
            st.rerun()

        # Initialize system with selected mode
        self.initialize_system(use_mock)

        # City Selection
        selected_city = st.sidebar.selectbox("Select City", CITIES)

        # Time Range Selection
        duration = st.sidebar.slider(
            "Select Time Range (minutes)",
            min_value=5,
            max_value=60,
            value=30,
            step=5
        )

        # Refresh Rate Selection
        refresh_rate = st.sidebar.select_slider(
            "Auto-refresh Interval",
            options=[5, 10, 15, 30, 60],
            value=15,
            help="Select how often to refresh the data (in seconds)"
        )

        # Display current mode
        st.sidebar.info(f"Currently using: {mode}")

        # Main content
        st.title(f"Weather Monitor - {selected_city}")

        # Mode indicator
        mode_color = "🟦" if use_mock else "🟩"
        st.markdown(f"{mode_color} Running in **{mode}** mode")

        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "Current Weather",
            "Analysis",
            "Alerts",
            "Data Details"
        ])

        with tab1:
            self.show_current_weather(selected_city)

        with tab2:
            self.show_weather_analysis(selected_city, duration)

        with tab3:
            self.show_alerts(selected_city)

        with tab4:
            self.show_data_details(selected_city, use_mock)

        # Auto-refresh mechanism
        if st.sidebar.button('Manual Refresh'):
            st.rerun()

        # Display time until next refresh
        refresh_placeholder = st.sidebar.empty()
        if st.sidebar.checkbox('Enable Auto-refresh', value=True):
            time_until_refresh = refresh_rate
            while time_until_refresh > 0:
                refresh_placeholder.text(f"Next refresh in {time_until_refresh} seconds")
                time.sleep(1)
                time_until_refresh -= 1
            st.rerun()

    def show_current_weather(self, city):
        # Get latest weather data
        end_date = datetime.now()
        start_date = end_date - timedelta(minutes=5)
        latest_data = self.db_ops.get_weather_data(city, start_date, end_date)

        if latest_data and len(latest_data) > 0:
            latest = latest_data[-1]

            # Create weather card
            weather_card = st.container()
            with weather_card:
                # Create three columns for current weather display
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Temperature",
                        f"{latest.temp:.1f}°C",
                        f"{latest.feels_like - latest.temp:+.1f}°C feels like",
                        delta_color="off"
                    )

                with col2:
                    st.metric("Condition", latest.main)

                with col3:
                    st.metric("Description", latest.description)

                # Show last update time with formatting
                st.markdown(f"""
                    <div style='text-align: right; color: gray; font-size: 0.8em;'>
                        Last updated: {latest.dt.strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No current weather data available")

    def show_weather_analysis(self, city, duration):
        end_date = datetime.now()
        start_date = end_date - timedelta(minutes=duration)

        # Get weather data
        data = self.db_ops.get_weather_data(city, start_date, end_date)

        if data:
            # Convert to DataFrame
            df = pd.DataFrame([{
                'datetime': d.dt,
                'temperature': d.temp,
                'feels_like': d.feels_like,
                'condition': d.main
            } for d in data])

            # Temperature trend
            fig_temp = px.line(
                df,
                x='datetime',
                y=['temperature', 'feels_like'],
                title=f'Temperature Trend - Last {duration} minutes',
                labels={'value': 'Temperature (°C)', 'datetime': 'Time'},
                template="plotly_white"
            )

            # Customize the layout
            fig_temp.update_layout(
                hovermode='x unified',
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )

            # Add threshold line
            fig_temp.add_hline(
                y=ALERT_THRESHOLD,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Alert Threshold ({ALERT_THRESHOLD}°C)"
            )

            st.plotly_chart(fig_temp, use_container_width=True)

            # Weather condition distribution
            condition_counts = df['condition'].value_counts()
            fig_dist = px.pie(
                values=condition_counts.values,
                names=condition_counts.index,
                title='Weather Condition Distribution',
                template="plotly_white"
            )
            st.plotly_chart(fig_dist, use_container_width=True)

            # Statistics in a nice format
            st.subheader("Temperature Statistics")
            stats_container = st.container()
            with stats_container:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Average Temperature",
                        f"{df['temperature'].mean():.1f}°C"
                    )
                with col2:
                    st.metric(
                        "Maximum Temperature",
                        f"{df['temperature'].max():.1f}°C",
                        f"+{df['temperature'].max() - df['temperature'].mean():.1f}°C from avg"
                    )
                with col3:
                    st.metric(
                        "Minimum Temperature",
                        f"{df['temperature'].min():.1f}°C",
                        f"{df['temperature'].min() - df['temperature'].mean():.1f}°C from avg"
                    )

        else:
            st.warning("No data available for the selected duration")

    def show_alerts(self, city):
        # Get data for the last hour to show recent alerts
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=1)
        data = self.db_ops.get_weather_data(city, start_date, end_date)

        if data:
            # Find temperature spikes above threshold
            alerts = [d for d in data if d.temp > ALERT_THRESHOLD]

            if alerts:
                st.warning(f"⚠️ Found {len(alerts)} temperature alerts in the last hour")

                # Create an expandable section for detailed alerts
                with st.expander("View Alert Details", expanded=True):
                    for alert in alerts:
                        st.markdown(f"""
                        ---
                        ### 🌡️ Temperature Alert
                        - **Time:** {alert.dt.strftime('%Y-%m-%d %H:%M:%S')}
                        - **Temperature:** {alert.temp:.1f}°C
                        - **Condition:** {alert.main}
                        - **Description:** {alert.description}
                        """)
            else:
                st.success("✅ No temperature alerts in the last hour")
        else:
            st.info("ℹ️ No alert data available")

    def show_data_details(self, city, use_mock):
        st.subheader("Data Source Information")

        # Create info cards
        info_container = st.container()
        with info_container:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                    ### System Configuration
                    - **Data Mode:** {}
                    - **Database:** {}
                    - **Temperature Unit:** {}
                    - **Alert Threshold:** {}°C
                """.format(
                    "Mock Data" if use_mock else "Real-time Data",
                    "SQLite (Mock)" if use_mock else "SQLite (Real)",
                    TEMPERATURE_UNIT,
                    ALERT_THRESHOLD
                ))

            with col2:
                st.markdown("""
                    ### Data Collection Details
                    - **City:** {}
                    - **Update Interval:** {} seconds
                    - **Database Location:** {}
                """.format(
                    city,
                    "10 (Mock)" if use_mock else "300 (Real)",
                    os.path.abspath('mock_weather_data.db' if use_mock else 'real_weather_data.db')
                ))

        # Show recent data entries
        st.subheader("Recent Data Entries")
        end_date = datetime.now()
        start_date = end_date - timedelta(minutes=10)
        recent_data = self.db_ops.get_weather_data(city, start_date, end_date)

        if recent_data:
            df = pd.DataFrame([{
                'Timestamp': d.dt,
                'Temperature (°C)': d.temp,
                'Feels Like (°C)': d.feels_like,
                'Condition': d.main,
                'Description': d.description
            } for d in recent_data])

            st.dataframe(df, use_container_width=True)
        else:
            st.info("No recent data entries available")


if __name__ == "__main__":
    app = StreamlitWeatherApp()
    app.run()