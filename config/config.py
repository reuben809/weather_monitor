from dotenv import load_dotenv
import os

load_dotenv()

# Database URLs
DATABASE_URL_MOCK = 'sqlite:///mock_weather_data.db'
DATABASE_URL_REAL = 'sqlite:///real_weather_data.db'

# API Configuration
API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# General Configuration
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
UPDATE_INTERVAL = 10  # seconds
TEMPERATURE_UNIT = 'celsius'
ALERT_THRESHOLD = 30  # Celsius
CONSECUTIVE_ALERTS = 2