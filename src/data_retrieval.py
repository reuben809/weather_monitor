import requests
from typing import Dict, Any, Optional
from config.config import API_KEY, BASE_URL, CITIES


def get_weather_data(city: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve weather data for a specific city from the OpenWeatherMap API.

    Args:
        city: Name of the city

    Returns:
        Weather data dictionary or None if retrieval fails
    """
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data for {city}: {str(e)}")
        return None


def fetch_all_cities() -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Retrieve weather data for all configured cities.

    Returns:
        Dictionary mapping city names to their weather data
    """
    return {city: get_weather_data(city) for city in CITIES}


def validate_api_key() -> bool:
    """
    Validate the OpenWeatherMap API key.

    Returns:
        True if the API key is valid, False otherwise
    """
    if not API_KEY:
        print("API key not found. Please check your .env file.")
        return False

    try:
        # Test the API key with a sample request
        response = requests.get(
            BASE_URL,
            params={'q': CITIES[0], 'appid': API_KEY, 'units': 'metric'},
            timeout=10
        )
        response.raise_for_status()
        return True
    except requests.RequestException:
        print("Invalid API key or API request failed. Please check your API key.")
        return False
