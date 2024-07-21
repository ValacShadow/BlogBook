# models/follow.py
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional

class FollowModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    follower_id: str
    following_id: str

    class Config:
        orm_mode = True
