# models/discussion.py
from bson import ObjectId

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class DiscussionModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    user_id: str
    text: str
    image_url: Optional[str] = None
    hashtags: List[str]
    created_on: Optional[str] = None
    modified_on: Optional[str] = None
    views: int = 0
    likes: int = 0

    class Config:
        from_attributes = True

# class DiscussionResponseModel(BaseModel):
#     id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
#     user_id: str
#     text: str
#     image_url: Optional[str] = None
#     hashtags: List[str]
#     created_on: Optional[str] = None
#     modified_on: Optional[str] = None
#     views: int = 0

#     class Config:
#         from_attributes = True
