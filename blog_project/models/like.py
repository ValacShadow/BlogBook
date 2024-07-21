# models/like.py
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LikeModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    discussion_id: Optional[str] = None
    comment_id: Optional[str] = None
    user_id: str
    created_on: Optional[str] = None

    class Config:
        from_attributes = True
