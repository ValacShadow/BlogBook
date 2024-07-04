from pydantic import BaseModel
from typing import List, Optional

class DiscussionModel(BaseModel):
    user_id: str
    text: str
    image_url: Optional[str] = None
    hashtags: List[str]
    created_on: Optional[str] = None
    modified_on: Optional[str] = None