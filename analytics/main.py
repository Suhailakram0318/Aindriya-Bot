from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import UsageStat, PerformanceMetric, ErrorLog
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Chatbot Analytics API",
    description="Tracks usage, performance, engagement, and errors."
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Usage Statistics ------------------ #

@app.get("/analytics/usage")
def get_usage_stats(db: Session = Depends(get_db)):
    stats = db.query(UsageStat).order_by(UsageStat.timestamp.desc()).all()
    return [
        {
            "user_id": stat.user_id,
            "username": stat.username,
            "endpoint": stat.endpoint,
            "request_type": stat.request_type,
            "timestamp": stat.timestamp
        }
        for stat in stats
    ]


# ------------------ Performance Metrics ------------------ #

@app.get("/analytics/performance")
def get_performance_metrics(db: Session = Depends(get_db)):
    metrics = db.query(PerformanceMetric).order_by(PerformanceMetric.timestamp.desc()).all()
    return [
        {
            "user_id": metric.user_id,
            "username": metric.username,
            "endpoint": metric.endpoint,
            "response_time": metric.response_time,
            "timestamp": metric.timestamp
        }
        for metric in metrics
    ]


# ------------------ Error Logs ------------------ #

@app.get("/analytics/errors")
def get_error_logs(db: Session = Depends(get_db)):
    logs = db.query(ErrorLog).order_by(ErrorLog.timestamp.desc()).all()
    return [
        {
            "user_id": log.user_id,
            "username": log.username,
            "endpoint": log.endpoint,
            "error_message": log.error_message,
            "timestamp": log.timestamp
        }
        for log in logs
    ]


# ------------------ Summary ------------------ #

@app.get("/analytics/summary")
def get_summary(db: Session = Depends(get_db)):
    total_usage = db.query(UsageStat).count()
    total_errors = db.query(ErrorLog).count()
    avg_response_time = db.query(PerformanceMetric).with_entities(
        func.avg(PerformanceMetric.response_time)
    ).scalar() or 0.0

    return {
        "total_usage_requests": total_usage,
        "total_errors": total_errors,
        "average_response_time_sec": round(avg_response_time, 3)
    }
