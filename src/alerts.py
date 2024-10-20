from config.config import ALERT_THRESHOLD, CONSECUTIVE_ALERTS
class AlertSystem:
    def __init__(self):
        self.alert_count = {}

    def check_alert(self, city, temp):
        if temp > ALERT_THRESHOLD:
            self.alert_count[city] = self.alert_count.get(city, 0) + 1
            if self.alert_count[city] >= CONSECUTIVE_ALERTS:
                self._trigger_alert(city, temp)
                self.alert_count[city] = 0
        else:
            self.alert_count[city] = 0

    def _trigger_alert(self, city, temp):
        print(
            f"ALERT: Temperature in {city} has exceeded {ALERT_THRESHOLD}°C for {CONSECUTIVE_ALERTS} consecutive updates. Current temperature: {temp}°C")
        # Here you could implement email notifications or other alert mechanisms
