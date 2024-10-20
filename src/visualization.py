# src/visualization.py
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from typing import Optional, Dict, List
import numpy as np
from src.database.db_operations import DatabaseOperations


class WeatherVisualizer:
    def __init__(self, output_dir: str = 'visualizations', db_ops: Optional[DatabaseOperations] = None):
        """Initialize visualizer with output directory and database operations."""
        self.output_dir = output_dir
        self.db_ops = db_ops
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """Ensure visualization directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def plot_temperature_trend(self, city: str, duration_minutes: int = 5) -> Optional[str]:
        """
        Plot temperature trend for a city over the specified duration.
        Returns the file path of the saved plot.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(minutes=duration_minutes)

        if not self.db_ops:
            print("Database operations not initialized")
            return None

        data_points = self.db_ops.get_weather_data(city, start_date, end_date)

        if not data_points:
            print(f"No data available for {city} in the last {duration_minutes} minutes")
            return None

        # Extract data
        times = [point.dt for point in data_points]
        temps = [point.temp for point in data_points]

        # Create plot
        plt.figure(figsize=(12, 6))
        plt.plot(times, temps, marker='o', linestyle='-', linewidth=2, color='#1f77b4')
        plt.title(f'Temperature Trend for {city}\nLast {duration_minutes} minutes', pad=20)
        plt.xlabel('Time')
        plt.ylabel('Temperature (°C)')
        plt.grid(True, linestyle='--', alpha=0.7)

        # Format x-axis
        plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)

        # Add shading for temperature ranges
        plt.axhspan(30, 40, color='red', alpha=0.1, label='Hot')
        plt.axhspan(20, 30, color='yellow', alpha=0.1, label='Moderate')
        plt.axhspan(10, 20, color='blue', alpha=0.1, label='Cool')
        plt.legend()

        plt.tight_layout()

        # Save plot
        filepath = os.path.join(self.output_dir, f'{city}_temperature_trend.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def plot_weather_distribution(self, city: str, duration_minutes: int = 5) -> Optional[str]:
        """
        Plot weather condition distribution for a city over the specified duration.
        Returns the file path of the saved plot.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(minutes=duration_minutes)

        if not self.db_ops:
            print("Database operations not initialized")
            return None

        data_points = self.db_ops.get_weather_data(city, start_date, end_date)

        if not data_points:
            print(f"No data available for {city} in the last {duration_minutes} minutes")
            return None

        # Count weather conditions
        conditions: Dict[str, int] = {}
        for point in data_points:
            if point.main:
                conditions[point.main] = conditions.get(point.main, 0) + 1

        if not conditions:
            print(f"No weather conditions data available for {city}")
            return None

        # Color mapping for weather conditions
        color_map = {
            'Clear': '#FDB813',
            'Clouds': '#B4B4B4',
            'Rain': '#4A90E2',
            'Thunderstorm': '#2C3E50',
            'Snow': '#FFFFFF',
            'Mist': '#D3D3D3'
        }

        # Create plot
        plt.figure(figsize=(10, 10))
        colors = [color_map.get(condition, '#808080') for condition in conditions.keys()]

        plt.pie(
            conditions.values(),
            labels=conditions.keys(),
            autopct='%1.1f%%',
            colors=colors,
            shadow=True,
            startangle=90
        )

        plt.title(f'Weather Distribution for {city}\nLast {duration_minutes} minutes', pad=20)

        # Save plot
        filepath = os.path.join(self.output_dir, f'{city}_weather_distribution.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath