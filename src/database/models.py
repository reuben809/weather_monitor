from sqlalchemy import Column, Integer, Float, String, DateTime, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WeatherData(Base):
    __tablename__ = 'weather_data'
    id = Column(Integer, primary_key=True)
    city = Column(String, nullable=False)
    main = Column(String)
    description = Column(String)
    temp = Column(Float)
    feels_like = Column(Float)
    dt = Column(DateTime)
    data_source = Column(String)  # 'mock' or 'real'

class DailySummary(Base):
    __tablename__ = 'daily_summaries'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    city = Column(String, nullable=False)
    avg_temp = Column(Float)
    max_temp = Column(Float)
    min_temp = Column(Float)
    dominant_condition = Column(String)
    dominant_condition_count = Column(Integer)
    total_observations = Column(Integer)
    data_source = Column(String)  # 'mock' or 'real'