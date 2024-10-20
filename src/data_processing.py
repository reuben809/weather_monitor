from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import Counter


def process_weather_data(data: Dict[str, Any], unit: str = 'celsius') -> Optional[Dict[str, Any]]:
    """
    Process raw weather data into a standardized format.

    Args:
        data: Raw weather data dictionary
        unit: Temperature unit ('celsius' or 'fahrenheit')

    Returns:
        Processed weather data dictionary or None if processing fails
    """
    try:
        if not data or 'main' not in data or 'weather' not in data or 'name' not in data:
            return None

        temp = data['main'].get('temp')
        feels_like = data['main'].get('feels_like')

        # Convert temperature if needed
        if unit == 'fahrenheit':
            temp = (temp * 9 / 5) + 32 if temp is not None else None
            feels_like = (feels_like * 9 / 5) + 32 if feels_like is not None else None

        processed_data = {
            'city': data['name'],
            'main': data['weather'][0].get('main'),
            'description': data['weather'][0].get('description'),
            'temp': round(temp, 2) if temp is not None else None,
            'feels_like': round(feels_like, 2) if feels_like is not None else None,
            'dt': datetime.fromtimestamp(data.get('dt', datetime.now().timestamp()))
        }

        # Ensure all required keys are present
        if not all(key in processed_data for key in ['city', 'temp', 'dt']):
            return None

        return processed_data

    except Exception as e:
        print(f"Error processing weather data: {str(e)}")
        return None


def calculate_daily_summary(data_points: List[Any]) -> Optional[List[Dict[str, Any]]]:
    """
    Calculate daily weather summaries from a list of weather data points.

    Args:
        data_points: List of WeatherData objects

    Returns:
        List of daily summary dictionaries or None if calculation fails
    """
    try:
        if not data_points:
            return None

        # Group data points by date and city
        daily_data: Dict[tuple, List[Any]] = {}
        for point in data_points:
            date = point.dt.date()
            city = point.city
            key = (date, city)

            if key not in daily_data:
                daily_data[key] = []
            daily_data[key].append(point)

        summaries = []
        for (date, city), points in daily_data.items():
            temps = [point.temp for point in points if point.temp is not None]
            conditions = [point.main for point in points if point.main is not None]

            if not temps or not conditions:
                continue

            # Find the most common weather condition
            condition_counts = Counter(conditions)
            dominant_condition = condition_counts.most_common(1)[0]

            summary = {
                'date': date,
                'city': city,
                'avg_temp': round(sum(temps) / len(temps), 2),
                'max_temp': round(max(temps), 2),
                'min_temp': round(min(temps), 2),
                'dominant_condition': dominant_condition[0],
                'dominant_condition_count': dominant_condition[1],
                'total_observations': len(points)
            }
            summaries.append(summary)

        return summaries if summaries else None

    except Exception as e:
        print(f"Error calculating daily summary: {str(e)}")
        return None
