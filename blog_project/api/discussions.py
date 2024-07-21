import os
import json
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form, status
from fastapi.security import OAuth2PasswordBearer

from models.discussion import DiscussionModel
from models.comment import CommentModel
from models.like import LikeModel
from models.user import UserModel
from services.db_connection import discussion_collection, user_collection, comment_collection, like_collection, hashtag_collection
from services.aws_s3_service import upload_image
from api.helper import get_current_user

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/discussions/", response_model=DiscussionModel, status_code=status.HTTP_201_CREATED)
async def create_discussion(
    text: str = Form(...),
    hashtags: str = Form(...),
    file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    hashtags_list = hashtags.split(',')
    tmp_dir = "tmp"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    image_url = None
    if file:
        file_location = os.path.join(tmp_dir, file.filename)
        with open(file_location, "wb") as buffer:
            buffer.write(file.file.read())
        image_url = upload_image(file_location)
        os.remove(file_location)

    now = datetime.now().isoformat()
    discussion = DiscussionModel(
        user_id=str(current_user["_id"]),
        text=text,
        image_url=image_url,
        hashtags=hashtags_list,
        created_on=now,
        modified_on=now
    )

    await discussion_collection.insert_one(discussion.model_dump())
    return discussion

@router.get("/discussions", response_model=List[DiscussionModel], status_code=status.HTTP_200_OK)
async def get_user_discussions(
    current_user: dict = Depends(get_current_user)
):
    discussions = await discussion_collection.find({"user_id": str(current_user["_id"])}).to_list(None)
    return discussions

@router.put("/discussions/{discussion_id}", response_model=DiscussionModel, status_code=status.HTTP_200_OK)
async def update_discussion(
    discussion_id: str,
    text: Optional[str] = Form(None),
    hashtags: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    discussion = await discussion_collection.find_one({"id": (discussion_id)})
    if discussion is None:
        raise HTTPException(status_code=404, detail="Discussion not found")
    if discussion["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to update this discussion")

    if text:
        discussion["text"] = text
    if hashtags:
        discussion["hashtags"] = hashtags.split(',')
    if file:
        tmp_dir = "tmp"
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        file_location = os.path.join(tmp_dir, file.filename)
        with open(file_location, "wb") as buffer:
            buffer.write(file.file.read())
        discussion["image_url"] = upload_image(file_location)
        os.remove(file_location)
    
    discussion["modified_on"] = datetime.now().isoformat()

    await discussion_collection.replace_one({"id":(discussion_id)}, discussion)
    return discussion

@router.delete("/discussions/{discussion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discussion(
    discussion_id: str,
    current_user: dict = Depends(get_current_user)
):
    discussion = await discussion_collection.find_one({"id": (discussion_id)})
    if discussion is None:
        raise HTTPException(status_code=404, detail="Discussion not found")
    if discussion["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to delete this discussion")

    await discussion_collection.delete_one({"id": (discussion_id)})
    return {"detail": "Discussion deleted"}

@router.post("/discussions/{discussion_id}/comments", response_model=CommentModel)
async def add_comment(
    discussion_id: str,
    text: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    now = datetime.now().isoformat()
    comment = CommentModel(
        discussion_id=discussion_id,
        user_id=str(current_user["_id"]),
        text=text,
        created_on=now,
        modified_on=now
    )

    await comment_collection.insert_one(comment.model_dump())
    return comment

@router.put("/discussions/{discussion_id}/comments/{comment_id}", response_model=CommentModel)
async def update_comment(
    discussion_id: str,
    comment_id: str,
    text: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    comment = await comment_collection.find_one({"id": (comment_id), "discussion_id": discussion_id})
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    comment["text"] = text
    comment["modified_on"] = datetime.now().isoformat()

    await comment_collection.replace_one({"id": (comment_id)}, comment)
    return comment

@router.delete("/discussions/{discussion_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    discussion_id: str,
    comment_id: str,
    current_user: dict = Depends(get_current_user)
):
    comment = await comment_collection.find_one({"id": (comment_id), "discussion_id": discussion_id})
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment["user_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    await comment_collection.delete_one({"id": (comment_id)})
    return {"detail": "Comment deleted"}

@router.post("/discussions/{discussion_id}/like", response_model=DiscussionModel)
async def like_discussion(
    discussion_id: str,
    current_user: dict = Depends(get_current_user)
):
    discussion = await discussion_collection.find_one({"id": (discussion_id)})
    # print("discussion", discussion)
    if discussion is None:
        raise HTTPException(status_code=404, detail="Discussion not found")

    like = await like_collection.find_one({"discussion_id": discussion_id, "user_id": str(current_user["_id"])})
    # print("like", like)
    if like is None:
        # print("in like")
        now = datetime.now().isoformat()
        like = LikeModel(
            discussion_id=discussion_id,
            user_id=str(str(current_user["_id"])),
            created_on=now
        )
       
        if "likes" in  discussion: 
            discussion["likes"] += 1
        else:
            discussion["likes"] = 1
            
        await like_collection.insert_one(like.model_dump())
        await discussion_collection.replace_one({"id": (discussion_id)}, discussion)
    return discussion

@router.post("/discussions/comments/{comment_id}/like", response_model=CommentModel)
async def like_comment(
    comment_id: str,
    current_user: dict = Depends(get_current_user)
):
    comment = await comment_collection.find_one({"id": (comment_id)})
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    like = await like_collection.find_one({"comment_id": comment_id, "user_id": str(current_user["_id"])})
    if like is None:
        now = datetime.now().isoformat()
        like = LikeModel(
            comment_id=comment_id,
            user_id=str(current_user["_id"]),
            created_on=now
        )
        await like_collection.insert_one(like.model_dump())
        comment["likes"] += 1
        await comment_collection.replace_one({"id": (comment_id)}, comment)
    return comment

@router.get("/discussions/{discussion_id}", response_model=DiscussionModel)
async def view_discussion(
    discussion_id: str,
    current_user: dict = Depends(get_current_user)
):
    
    # print("in get", discussion_id)
    discussion = await discussion_collection.find_one({"id":(discussion_id)})
    if discussion is None:
        raise HTTPException(status_code=404, detail="Discussion not found")
    if discussion["user_id"] != str(current_user["_id"]):
        # print("In view", discussion["user_id"], current_user["_id"])
        discussion["views"] += 1
        await discussion_collection.replace_one({"id": (discussion_id)}, discussion)
    return discussion

@router.get("/discussions/{discussion_id}/comments", response_model=List[CommentModel], status_code=status.HTTP_200_OK)
async def get_discussion_comments(
    discussion_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Fetch comments
    comments = await comment_collection.find({"discussion_id": discussion_id}).to_list(None)
    
    # For each comment, fetch likes and replies
    for comment in comments:
        comment["replies"] = await comment_collection.find({"parent_comment_id": str(comment["id"])}).to_list(None)
        for reply in comment["replies"]:
            reply["likes"] = await like_collection.count_documents({"comment_id": str(reply["id"])})

    return comments
