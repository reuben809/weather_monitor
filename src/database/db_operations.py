from datetime import datetime
from src.database.models import WeatherData, DailySummary
from typing import Dict, List, Any

class DatabaseOperations:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def store_weather_data(self, data: Dict[str, Any]):
        """Store weather data in the database."""
        if not data:
            return

        session = self.db_manager.get_session()
        try:
            data['data_source'] = self.db_manager.data_source
            weather_data = WeatherData(**data)
            session.add(weather_data)
            session.commit()
        except Exception as e:
            print(f"Error storing weather data: {str(e)}")
            session.rollback()
        finally:
            session.close()

    def store_daily_summaries(self, summaries: List[Dict[str, Any]]):
        """Store daily summaries in the database."""
        if not summaries:
            return

        session = self.db_manager.get_session()
        try:
            for summary in summaries:
                summary['data_source'] = self.db_manager.data_source
                existing_summary = session.query(DailySummary).filter(
                    DailySummary.date == summary['date'],
                    DailySummary.city == summary['city'],
                    DailySummary.data_source == self.db_manager.data_source
                ).first()

                if existing_summary:
                    for key, value in summary.items():
                        setattr(existing_summary, key, value)
                else:
                    daily_summary = DailySummary(**summary)
                    session.add(daily_summary)

            session.commit()
        except Exception as e:
            print(f"Error storing daily summaries: {str(e)}")
            session.rollback()
        finally:
            session.close()

    def get_weather_data(self, city: str, start_date: datetime, end_date: datetime):
        """Retrieve weather data for a specific city and date range."""
        session = self.db_manager.get_session()
        try:
            return session.query(WeatherData).filter(
                WeatherData.city == city,
                WeatherData.dt.between(start_date, end_date),
                WeatherData.data_source == self.db_manager.data_source
            ).all()
        finally:
            session.close()

    def get_daily_summaries(self, city: str, start_date: datetime, end_date: datetime):
        """Retrieve daily summaries for a specific city and date range."""
        session = self.db_manager.get_session()
        try:
            return session.query(DailySummary).filter(
                DailySummary.city == city,
                DailySummary.date.between(start_date, end_date),
                DailySummary.data_source == self.db_manager.data_source
            ).all()
        finally:
            session.close()