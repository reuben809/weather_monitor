import unittest
from datetime import datetime
from src.data_processing import (
    kelvin_to_celsius,
    kelvin_to_fahrenheit,
    process_weather_data,
    calculate_daily_summary
)


class TestDataProcessing(unittest.TestCase):
    def setUp(self):
        self.sample_data = {
            'name': 'Test City',
            'main': {'temp': 300.15, 'feels_like': 305.15},
            'weather': [{'main': 'Clear', 'description': 'clear sky'}],
            'dt': int(datetime.now().timestamp())
        }

    def test_temperature_conversion(self):
        """Test temperature conversion functions."""
        kelvin = 300.15
        self.assertAlmostEqual(kelvin_to_celsius(kelvin), 27, places=1)
        self.assertAlmostEqual(kelvin_to_fahrenheit(kelvin), 80.6, places=1)

    def test_process_weather_data(self):
        """Test weather data processing."""
        processed = process_weather_data(self.sample_data, 'celsius')
        self.assertIsNotNone(processed)
        self.assertEqual(processed['city'], 'Test City')
        self.assertEqual(processed['main'], 'Clear')
        self.assertAlmostEqual(processed['temp'], 27, places=1)

    def test_calculate_daily_summary(self):
        """Test daily summary calculation."""
        data_list = [
            {
                'city': 'Test City',
                'temp': 25.0,
                'main': 'Clear',
                'dt': datetime.now()
            },
            {
                'city': 'Test City',
                'temp': 27.0,
                'main': 'Clear',
                'dt': datetime.now()
            }
        ]

        summary = calculate_daily_summary(data_list)
        self.assertIsNotNone(summary)
        self.assertEqual(summary['city'], 'Test City')
        self.assertEqual(summary['avg_temp'], 26.0)
        self.assertEqual(summary['max_temp'], 27.0)
        self.assertEqual(summary['min_temp'], 25.0)
        self.assertEqual(summary['dominant_condition'], 'Clear')