import unittest
from src.alerts import AlertSystem


class TestAlertSystem(unittest.TestCase):
    def setUp(self):
        self.alert_system = AlertSystem()
        self.city = "Test City"

    def test_threshold_setting(self):
        """Test setting custom thresholds."""
        self.alert_system.set_threshold('temperature', 30.0)
        self.assertEqual(self.alert_system.thresholds['temperature'], 30.0)

    def test_alert_triggering(self):
        """Test alert triggering conditions."""
        # Set lower threshold for testing
        self.alert_system.set_threshold('temperature', 30.0)
        self.alert_system.set_threshold('consecutive_count', 2)

        # First high temperature reading
        result = self.alert_system.check_alert(self.city, 31.0)
        self.assertIsNone(result)  # No alert yet

        # Second high temperature reading should trigger alert
        result = self.alert_system.check_alert(self.city, 31.0)
        self.assertIsNotNone(result)
        self.assertEqual(result['city'], self.city)
        self.assertEqual(result['temperature'], 31.0)

    def test_alert_reset(self):
        """Test alert count reset on normal temperature."""
        self.alert_system.set_threshold('temperature', 30.0)

        # One high temperature reading
        self.alert_system.check_alert(self.city, 31.0)

        # Normal temperature should reset count
        self.alert_system.check_alert(self.city, 25.0)
        self.assertEqual(self.alert_system.alert_count.get(self.city, 0), 0)