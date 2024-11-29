# schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., max_length=255)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    title: str = Field(..., max_length=255)
    body: str
    recipient_id: int

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    sender_id: int
    timestamp: datetime
    is_read: bool

    class Config:
        orm_mode = True
