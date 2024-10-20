import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import math



def generate_mock_weather_data(cities: List[str], start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """
    Generate mock weather data for specified cities and time range.

    Args:
        cities: List of city names
        start_date: Start datetime for data generation
        end_date: End datetime for data generation

    Returns:
        List of mock weather data dictionaries
    """
    weather_conditions = [
        ('Clear', 'clear sky'),
        ('Clouds', 'scattered clouds'),
        ('Rain', 'light rain'),
        ('Thunderstorm', 'thunderstorm'),
        ('Snow', 'light snow'),
        ('Mist', 'mist')
    ]

    data = []
    current_date = start_date

    # City-specific temperature ranges (min, max)
    city_temp_ranges = {
        'Delhi': (20, 45),
        'Mumbai': (24, 35),
        'Chennai': (24, 38),
        'Bangalore': (18, 32),
        'Kolkata': (22, 38),
        'Hyderabad': (20, 40)
    }

    while current_date <= end_date:
        for city in cities:
            # Get city-specific temperature range
            temp_range = city_temp_ranges.get(city, (15, 35))

            # Generate base temperature using sin wave for more realistic daily variation
            hour = current_date.hour
            daily_factor = (math.sin(hour * math.pi / 12 - math.pi / 2) + 1) / 2
            temp_range_size = temp_range[1] - temp_range[0]
            base_temp = temp_range[0] + (daily_factor * temp_range_size)

            # Add some random variation
            temp = base_temp + random.uniform(-2, 2)
            feels_like = temp + random.uniform(-2, 2)

            # Select weather condition with seasonal/temperature-based weighting
            if temp > 35:
                weights = [0.6, 0.3, 0.05, 0.05, 0, 0]  # More likely to be clear/cloudy
            elif temp < 15:
                weights = [0.2, 0.3, 0.2, 0.1, 0.1, 0.1]  # More varied conditions
            else:
                weights = [0.3, 0.3, 0.2, 0.1, 0.05, 0.05]  # Balanced distribution

            weather = random.choices(weather_conditions, weights=weights)[0]

            data_point = {
                'name': city,
                'main': {
                    'temp': round(temp, 2),
                    'feels_like': round(feels_like, 2)
                },
                'weather': [{
                    'main': weather[0],
                    'description': weather[1]
                }],
                'dt': int(current_date.timestamp())
            }

            data.append(data_point)

        current_date += timedelta(minutes=10)  # Generate data every 10 minutes

    return data


def get_seasonal_adjustments(date: datetime) -> Dict[str, float]:
    """
    Calculate seasonal temperature adjustments based on the date.

    Args:
        date: The date to calculate adjustments for

    Returns:
        Dictionary of adjustment factors for different weather parameters
    """
    # Day of year from 0 to 1
    day_of_year = date.timetuple().tm_yday
    season_factor = math.sin(2 * math.pi * (day_of_year / 365 - 0.25))

    return {
        'temp_adjustment': 5 * season_factor,  # ±5°C seasonal variation
        'clear_sky_prob': 0.4 + (0.2 * season_factor),  # Probability of clear sky
        'rain_prob': 0.2 - (0.1 * season_factor)  # Probability of rain
    }