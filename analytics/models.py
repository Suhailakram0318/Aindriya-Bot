from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from database import Base

Base = declarative_base()

class UsageStat(Base):
    __tablename__ = 'usage_stats'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    username = Column(String(50))
    endpoint = Column(String(100))
    request_type = Column(String(20))  
    timestamp = Column(DateTime, default=datetime.utcnow)


class PerformanceMetric(Base):
    __tablename__ = 'performance_metrics'

    id = Column(Integer, primary_key=True)
    endpoint = Column(String(100))
    response_time = Column(Float)
    user_id = Column(Integer)
    username = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)


class ErrorLog(Base):
    __tablename__ = 'error_logs'

    id = Column(Integer, primary_key=True)
    endpoint = Column(String(100))
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), nullable=True)
    error_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
