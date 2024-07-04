# api/discussions.py
from fastapi import APIRouter, HTTPException
from models.discussion import DiscussionModel
from services.db_connection import discussion_collection

router = APIRouter()

@router.post("/discussions/", response_model=DiscussionModel)
async def create_discussion(discussion: DiscussionModel):
    await discussion_collection.insert_one(discussion.dict())
    return discussion

# Similarly, define endpoints for update, delete, and get discussions.
