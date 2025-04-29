from datetime import datetime
from analytics.models import UsageStat, PerformanceMetric, ErrorLog
from sqlalchemy.orm import Session
import time

def log_usage(db: Session, user_id, username, endpoint, request_type):
    usage = UsageStat(
        user_id=user_id,
        username=username,
        endpoint=endpoint,
        request_type=request_type,
        timestamp=datetime.utcnow()
    )
    db.add(usage)
    db.commit()

def log_performance(db: Session, user_id, username, endpoint, response_time):
    perf = PerformanceMetric(
        user_id=user_id,
        username=username,
        endpoint=endpoint,
        response_time=response_time,
        timestamp=datetime.utcnow()
    )
    db.add(perf)
    db.commit()

def log_error(db: Session, endpoint, error_message, user_id=None, username=None):
    err = ErrorLog(
        endpoint=endpoint,
        error_message=error_message,
        user_id=user_id,
        username=username,
        timestamp=datetime.utcnow()
    )
    db.add(err)
    db.commit()
