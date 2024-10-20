import time
from datetime import datetime, timedelta
import sys
import os
from typing import List, Dict, Any, Optional

from config.config import (
    DATABASE_URL_MOCK,
    DATABASE_URL_REAL,
    UPDATE_INTERVAL,
    CITIES,
    TEMPERATURE_UNIT
)
from src.database.db_manager import DatabaseManager
from src.database.db_operations import DatabaseOperations
from src.alerts import AlertSystem
from src.visualization import WeatherVisualizer
from src.data_processing import process_weather_data, calculate_daily_summary
from src.mock_data_generator import generate_mock_weather_data
from src.data_retrieval import fetch_all_cities


class WeatherApp:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.db_manager = DatabaseManager(
            DATABASE_URL_MOCK if use_mock else DATABASE_URL_REAL,
            'mock' if use_mock else 'real'
        )
        self.db_ops = DatabaseOperations(self.db_manager)
        self.alert_system = AlertSystem()
        self.visualizer = WeatherVisualizer(db_ops=self.db_ops)
        self.daily_data = {city: [] for city in CITIES}

    def setup(self) -> bool:
        """Initialize the application."""
        try:
            os.makedirs('visualizations', exist_ok=True)
            return True
        except Exception as e:
            print(f"Error during setup: {str(e)}")
            return False

    def process_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Process weather data based on the selected source."""
        if self.use_mock:
            return self._process_mock_data(start_date, end_date)
        else:
            return self._process_real_data()

    def _process_mock_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Generate and process mock weather data."""
        print("\nGenerating and processing mock weather data...")
        mock_data = generate_mock_weather_data(CITIES, start_date, end_date)
        processed_data = []
        processed_count = 0

        for data in mock_data:
            processed = process_weather_data(data, TEMPERATURE_UNIT)
            if processed:
                self.db_ops.store_weather_data(processed)
                processed_data.append(processed)
                processed_count += 1
                self.daily_data[processed['city']].append(processed)
                self.alert_system.check_alert(processed['city'], processed['temp'])

        print(f"Processed {processed_count} mock weather records")
        return processed_data

    def _process_real_data(self) -> List[Dict[str, Any]]:
        """Fetch and process real-time weather data."""
        print("\nFetching real-time weather data...")
        all_city_data = fetch_all_cities()
        processed_data = []

        for city, data in all_city_data.items():
            if data:
                processed = process_weather_data(data, TEMPERATURE_UNIT)
                if processed:
                    self.db_ops.store_weather_data(processed)
                    processed_data.append(processed)
                    self.daily_data[city].append(processed)
                    self.alert_system.check_alert(city, processed['temp'])

        print(f"Processed {len(processed_data)} real-time weather records")
        return processed_data

    def run(self):
        """Main application loop."""
        print(f"Starting Weather Monitoring Application ({self.db_manager.data_source} data)")

        try:
            duration = self._get_visualization_duration()
            print(f"Visualizations will show data for the last {duration} minutes")

            if self.use_mock:
                self._run_mock_data(duration)
            else:
                self._run_real_time_data(duration)

        except Exception as e:
            print(f"An error occurred in the application: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def _run_mock_data(self, duration: int):
        """Run the application with mock data."""
        end_date = datetime.now()
        start_date = end_date - timedelta(minutes=duration)

        # Process all mock data at once
        self.process_data(start_date, end_date)

        # Generate daily summaries
        self._process_daily_summaries(start_date, end_date)

        # Generate visualizations
        self._generate_visualizations(duration)

        print("Mock data processing and visualization complete")

    def _run_real_time_data(self, duration: int):
        """Run the application with real-time data."""
        last_visualization_time = datetime.now()
        visualization_interval = 300  # 5 minutes in seconds

        while True:
            current_time = datetime.now()
            print(f"\nFetching weather data at {current_time}")

            # Process weather data
            self.process_data(current_time - timedelta(minutes=5), current_time)

            # Check if it's a new day
            if current_time.hour == 0 and current_time.minute < 5:
                self._process_daily_summaries(current_time - timedelta(days=1), current_time)
                self.daily_data = {city: [] for city in CITIES}

            # Check if it's time to create visualizations
            time_since_last_visualization = (current_time - last_visualization_time).total_seconds()
            if time_since_last_visualization >= visualization_interval:
                self._generate_visualizations(duration)
                last_visualization_time = current_time

            time.sleep(UPDATE_INTERVAL)

    def _get_visualization_duration(self) -> int:
        """Get user input for visualization duration."""
        while True:
            try:
                duration = int(input("Enter the duration (in minutes) for visualization (minimum 5): "))
                if duration >= 5:
                    return duration
                print("Duration must be at least 5 minutes.")
            except ValueError:
                print("Please enter a valid number.")

    def _process_daily_summaries(self, start_date: datetime, end_date: datetime):
        """Process and store daily summaries."""
        print("\nProcessing daily summaries...")

        for city in CITIES:
            try:
                city_data = self.db_ops.get_weather_data(city, start_date, end_date)
                if city_data:
                    summaries = calculate_daily_summary(city_data)
                    if summaries:
                        self.db_ops.store_daily_summaries(summaries)
                        self._display_summaries(city, summaries)
                    else:
                        print(f"No summaries generated for {city}")
                else:
                    print(f"No data available for {city}")
            except Exception as e:
                print(f"Error processing daily summaries for {city}: {str(e)}")

    def _generate_visualizations(self, duration: int):
        """Generate visualizations for all cities."""
        print("\nGenerating visualizations...")
        for city in CITIES:
            try:
                temp_plot = self.visualizer.plot_temperature_trend(city, duration)
                dist_plot = self.visualizer.plot_weather_distribution(city, duration)

                if temp_plot and dist_plot:
                    print(f"Generated visualizations for {city}")
                else:
                    print(f"Some visualizations could not be generated for {city}")
            except Exception as e:
                print(f"Error generating visualizations for {city}: {str(e)}")
        print("Visualization update complete\n")

    def _display_summaries(self, city: str, summaries: List[Dict[str, Any]]):
        """Display daily summaries for a city."""
        print(f"\nDaily summaries for {city}:")
        for summary in summaries:
            print(f"  Date: {summary['date']}")
            print(f"  Average Temperature: {summary['avg_temp']:.2f}°C")
            print(f"  Max Temperature: {summary['max_temp']:.2f}°C")
            print(f"  Min Temperature: {summary['min_temp']:.2f}°C")
            print(f"  Dominant Condition: {summary['dominant_condition']}")
            print(f"  Total Observations: {summary['total_observations']}")
            print()


if __name__ == "__main__":
    # Set to False to use real-time data
    USE_MOCK_DATA = False


    app = WeatherApp(use_mock=USE_MOCK_DATA)
    if app.setup():
        app.run()
    else:
        print("Application setup failed. Exiting.")
        sys.exit(1)
# import time
# from datetime import datetime, timedelta
# import sys
# import os
# from typing import List, Dict, Any, Optional
#
# from config.config import (
#     DATABASE_URL_MOCK,
#     DATABASE_URL_REAL,
#     UPDATE_INTERVAL,
#     CITIES,
#     TEMPERATURE_UNIT
# )
# from src.database.db_manager import DatabaseManager
# from src.database.db_operations import DatabaseOperations
# from src.alerts import AlertSystem
# from src.visualization import WeatherVisualizer
# from src.data_processing import process_weather_data, calculate_daily_summary
# from src.mock_data_generator import generate_mock_weather_data
# from src.data_retrieval import fetch_all_cities
#
#
# class WeatherApp:
#     def __init__(self, use_mock: bool = True):
#         self.use_mock = use_mock
#         self.db_manager = DatabaseManager(
#             DATABASE_URL_MOCK if use_mock else DATABASE_URL_REAL,
#             'mock' if use_mock else 'real'
#         )
#         self.db_ops = DatabaseOperations(self.db_manager)
#         self.alert_system = AlertSystem()
#         self.visualizer = WeatherVisualizer(db_ops=self.db_ops)
#         self.daily_data = {city: [] for city in CITIES}
#         self.last_summary_time = datetime.now() - timedelta(minutes=10)
#
#     def setup(self) -> bool:
#         """Initialize the application."""
#         try:
#             os.makedirs('visualizations', exist_ok=True)
#             return True
#         except Exception as e:
#             print(f"Error during setup: {str(e)}")
#             return False
#
#     def process_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
#         """Process weather data based on the selected source."""
#         if self.use_mock:
#             return self._process_mock_data(start_date, end_date)
#         else:
#             return self._process_real_data()
#
#     def _process_mock_data(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
#         """Generate and process mock weather data."""
#         print("\nGenerating and processing mock weather data...")
#         mock_data = generate_mock_weather_data(CITIES, start_date, end_date)
#         processed_data = []
#         processed_count = 0
#
#         for data in mock_data:
#             processed = process_weather_data(data, TEMPERATURE_UNIT)
#             if processed:
#                 self.db_ops.store_weather_data(processed)
#                 processed_data.append(processed)
#                 processed_count += 1
#                 self.daily_data[processed['city']].append(processed)
#                 self.alert_system.check_alert(processed['city'], processed['temp'])
#
#         print(f"Processed {processed_count} mock weather records")
#         return processed_data
#
#     def _process_real_data(self) -> List[Dict[str, Any]]:
#         """Fetch and process real-time weather data."""
#         print("\nFetching real-time weather data...")
#         all_city_data = fetch_all_cities()
#         processed_data = []
#
#         for city, data in all_city_data.items():
#             if data:
#                 processed = process_weather_data(data, TEMPERATURE_UNIT)
#                 if processed:
#                     self.db_ops.store_weather_data(processed)
#                     processed_data.append(processed)
#                     self.daily_data[city].append(processed)
#                     self.alert_system.check_alert(city, processed['temp'])
#
#         print(f"Processed {len(processed_data)} real-time weather records")
#         return processed_data
#
#     def run(self):
#         """Main application loop."""
#         print(f"Starting Weather Monitoring Application ({self.db_manager.data_source} data)")
#
#         try:
#             duration = self._get_visualization_duration()
#             print(f"Visualizations will show data for the last {duration} minutes")
#
#             if self.use_mock:
#                 self._run_mock_data(duration)
#             else:
#                 self._run_real_time_data(duration)
#
#         except Exception as e:
#             print(f"An error occurred in the application: {str(e)}")
#             import traceback
#             traceback.print_exc()
#             sys.exit(1)
#
#     def _run_mock_data(self, duration: int):
#         """Run the application with mock data."""
#         end_date = datetime.now()
#         start_date = end_date - timedelta(minutes=duration)
#
#         # Process all mock data at once
#         self.process_data(start_date, end_date)
#
#         # Generate daily summaries
#         self._process_daily_summaries(start_date, end_date)
#
#         # Generate visualizations
#         self._generate_visualizations(duration)
#
#         print("Mock data processing and visualization complete")
#
#     def _run_real_time_data(self, duration: int):
#         """Run the application with real-time data."""
#         last_visualization_time = datetime.now()
#         visualization_interval = 60  # 1 minute in seconds for testing
#         summary_interval = 60  # 1 minute in seconds for testing
#
#         start_time = datetime.now()
#         while (datetime.now() - start_time).total_seconds() < duration * 60:
#             current_time = datetime.now()
#             print(f"\nFetching weather data at {current_time}")
#
#             # Process weather data
#             self.process_data(current_time - timedelta(minutes=5), current_time)
#
#             # Check if it's time to process daily summaries
#             time_since_last_summary = (current_time - self.last_summary_time).total_seconds()
#             if time_since_last_summary >= summary_interval:
#                 print("Processing daily summaries...")
#                 self._process_daily_summaries(current_time - timedelta(days=1), current_time)
#                 self.last_summary_time = current_time
#
#             # Check if it's time to create visualizations
#             time_since_last_visualization = (current_time - last_visualization_time).total_seconds()
#             if time_since_last_visualization >= visualization_interval:
#                 self._generate_visualizations(duration)
#                 last_visualization_time = current_time
#
#             time.sleep(UPDATE_INTERVAL)
#
#         print(f"Application ran for {duration} minutes. Exiting.")
#
#     def _get_visualization_duration(self) -> int:
#         """Get user input for visualization duration."""
#         while True:
#             try:
#                 duration = int(input("Enter the duration (in minutes) for visualization (minimum 5): "))
#                 if duration >= 5:
#                     return duration
#                 print("Duration must be at least 5 minutes.")
#             except ValueError:
#                 print("Please enter a valid number.")
#
#     def _process_daily_summaries(self, start_date: datetime, end_date: datetime):
#         """Process and store daily summaries."""
#         print("\nProcessing daily summaries...")
#
#         for city in CITIES:
#             try:
#                 # Fetch weather data for the city
#                 city_data = self.db_ops.get_weather_data(city, start_date, end_date)
#
#                 if city_data:
#                     # Calculate summaries
#                     summaries = calculate_daily_summary(city_data)
#
#                     if summaries:
#                         # Store each summary in the database
#                         for summary in summaries:
#                             success = self.db_ops.store_daily_summary(summary)
#                             if success:
#                                 print(f"Stored daily summary for {city} on {summary['date']}")
#                             else:
#                                 print(f"Failed to store daily summary for {city} on {summary['date']}")
#
#                         # Display the summaries
#                         self._display_summaries(city, summaries)
#                     else:
#                         print(f"No summaries generated for {city}")
#                 else:
#                     print(f"No data available for {city}")
#             except Exception as e:
#                 print(f"Error processing daily summaries for {city}: {str(e)}")
#
#     def _generate_visualizations(self, duration: int):
#         """Generate visualizations for all cities."""
#         print("\nGenerating visualizations...")
#         for city in CITIES:
#             try:
#                 temp_plot = self.visualizer.plot_temperature_trend(city, duration)
#                 dist_plot = self.visualizer.plot_weather_distribution(city, duration)
#
#                 if temp_plot and dist_plot:
#                     print(f"Generated visualizations for {city}")
#                 else:
#                     print(f"Some visualizations could not be generated for {city}")
#             except Exception as e:
#                 print(f"Error generating visualizations for {city}: {str(e)}")
#         print("Visualization update complete\n")
#
#     def _display_summaries(self, city: str, summaries: List[Dict[str, Any]]):
#         """Display daily summaries for a city."""
#         print(f"\nDaily summaries for {city}:")
#         for summary in summaries:
#             print(f"  Date: {summary['date']}")
#             print(f"  Average Temperature: {summary['avg_temp']:.2f}°C")
#             print(f"  Max Temperature: {summary['max_temp']:.2f}°C")
#             print(f"  Min Temperature: {summary['min_temp']:.2f}°C")
#             print(f"  Dominant Condition: {summary['dominant_condition']}")
#             print(f"  Total Observations: {summary['total_observations']}")
#             print()
#
#
# if __name__ == "__main__":
#     USE_MOCK_DATA = False
#
#     app = WeatherApp(use_mock=USE_MOCK_DATA)
#     if app.setup():
#         app.run()
#     else:
#         print("Application setup failed. Exiting.")
#         sys.exit(1)