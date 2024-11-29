# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    """
    Modelo para usuários do sistema.
    """
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    sent_messages = relationship('Message', back_populates='sender', foreign_keys='Message.sender_id')
    received_messages = relationship('Message', back_populates='recipient', foreign_keys='Message.recipient_id')

class Message(Base):
    """
    Modelo para mensagens enviadas entre usuários.
    """
    __tablename__ = 'Messages'

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    recipient_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    sender = relationship('User', back_populates='sent_messages', foreign_keys=[sender_id])
    recipient = relationship('User', back_populates='received_messages', foreign_keys=[recipient_id])
