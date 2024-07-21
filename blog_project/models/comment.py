# models/comment.py
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional, List

class CommentModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    discussion_id: str
    parent_comment_id: Optional[str] = None
    user_id: str
    text: str
    created_on: Optional[str] = None
    modified_on: Optional[str] = None
    likes: int = 0
    replies: List['CommentModel'] = []

    class Config:
        orm_mode = True

CommentModel.model_rebuild()
