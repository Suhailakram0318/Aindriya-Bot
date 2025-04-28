# models.py
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import Base

Base = declarative_base()

class QuestionPayload(BaseModel):
    user_id: int
    username: str
    question: str

# User table
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))

    # Relationships
    chats = relationship('ChatHistory', back_populates='user')
    documents = relationship('Document', back_populates='user')

    def __repr__(self):
        return f"<User {self.username}>"

class ChatHistory(Base):
    __tablename__ = 'chat_history'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    username = Column(String(50))
    message = Column(Text)
    timestamp = Column(String(255))

    user = relationship('User', back_populates='chats')

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
