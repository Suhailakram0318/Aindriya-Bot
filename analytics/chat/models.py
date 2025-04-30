# models.py
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from typing import Optional

Base = declarative_base()

class QuestionPayload(BaseModel):
    user_id: int
    username: str
    question: str
    session_id: Optional[int] = None

# User table
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))

    # Relationships
    chats = relationship('ChatHistory', back_populates='user')
    documents = relationship('Document', back_populates='user')
    sessions = relationship("Session", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"

class ChatHistory(Base):
    __tablename__ = 'chat_history'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    username = Column(String(50))
    message = Column(Text)
    timestamp = Column(String(255))
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)

    user = relationship('User', back_populates='chats')
    session = relationship("Session", back_populates="chat_history")

    def __repr__(self):
        return f"<ChatHistory {self.id} - {self.username}>"

class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    username = Column(String(50))
    doc_type = Column(String(50))  # 'text', 'pdf', 'url', etc.
    content = Column(Text)  # The content of the document
    timestamp = Column(String(255))

    user = relationship('User', back_populates='documents')

    def __repr__(self):
        return f"<Document {self.id} - {self.username}>"
    
class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    chat_history = relationship("ChatHistory", back_populates="session")

class AskRequest(BaseModel):
    user_id: int
    question: str
    session_id: Optional[int] = None
    