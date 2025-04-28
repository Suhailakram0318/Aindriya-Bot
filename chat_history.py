from datetime import datetime
from sqlalchemy.orm import Session
from models import ChatHistory, Document

def store_chat_history(db: Session, user_id: int, username: str, message: str) -> str:
    """Store the user's chat message."""
    chat_entry = ChatHistory(
        user_id=user_id,
        username=username,
        message=message,
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)
    return f"Chat message stored for user {username}"

def store_document(db: Session, user_id: int, username: str, doc_type: str, content: str) -> str:
    """Store documents (text, url, etc.) for training."""
    document_entry = Document(
        user_id=user_id,
        username=username,
        doc_type=doc_type,
        content=content,
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.add(document_entry)
    db.commit()
    db.refresh(document_entry)
    return f"Document of type {doc_type} stored for user {username}"