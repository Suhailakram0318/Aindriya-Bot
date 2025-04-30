from fastapi import FastAPI, Depends
from sqlalchemy import func, cast, Date
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from chat.models import ChatHistory, User


app = FastAPI(title="Chatbot Analytics API")


@app.get("/analytics/total_messages")
def total_messages(user_id: int, db: Session = Depends(get_db)):
    count = db.query(func.count(ChatHistory.id)).filter(ChatHistory.user_id == user_id).scalar()
    return {"user_id": user_id, "total_messages": count}


@app.get("/analytics/messages_per_day")
def messages_per_day(user_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(cast(ChatHistory.timestamp, Date), func.count())
        .filter(ChatHistory.user_id == user_id)
        .group_by(cast(ChatHistory.timestamp, Date))
        .all()
    )
    return [{"date": str(r[0]), "message_count": r[1]} for r in results]


@app.get("/analytics/recent_activity")
def recent_activity(days: int = 7, db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=days)
    results = (
        db.query(ChatHistory.user_id, func.count(ChatHistory.id))
        .filter(ChatHistory.timestamp >= since)
        .group_by(ChatHistory.user_id)
        .all()
    )
    return [{"user_id": r[0], "message_count": r[1]} for r in results]


@app.get("/analytics/user_summary/{user_id}")
def user_summary(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found."}

    total_messages = db.query(func.count(ChatHistory.id)).filter(ChatHistory.user_id == user_id).scalar()
    latest_message = db.query(ChatHistory.timestamp).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.timestamp.desc()).first()

    return {
        "user_id": user_id,
        "username": user.username,
        "total_messages": total_messages,
        "last_activity": latest_message[0] if latest_message else None,
    }
