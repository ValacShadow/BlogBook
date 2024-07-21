import json
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from models.user import UserModel, UserLoginModel, Token, TokenData, UserResponseModel
from models.follow import FollowModel
from services.db_connection import user_collection, follow_collection
from services.auth_service import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    decode_access_token
)
from services.redis_service import redis_client

from pydantic import EmailStr
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Security

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/signup", response_model=UserResponseModel, status_code=201)
async def signup(user: UserModel):
    existing_user = await user_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    user_data = user.model_dump()
    user_data["password"] = hashed_password
    
    try:
        await user_collection.insert_one(user_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # Remove sensitive data from response
    user_data.pop("password", None)

    return user_data


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username
    cached_user = redis_client.get(email)
    
    if cached_user:
        user = json.loads(cached_user)
    else:
        user = await user_collection.find_one({"email": email})
        if user:
            redis_client.set(email, json.dumps(user, default=str))
    
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    email: EmailStr = payload.get("sub")
    user = await user_collection.find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# User details endpoint
@router.get("/me", response_model=UserResponseModel)
async def get_me(token: str = Depends(oauth2_scheme)):
    """
    Get the details of the current user.

    Retrieves the user details from the database using the provided JWT token.
    First, it decodes the token and extracts the email from the payload. Then, it checks if the user
    exists in the cache. If it does, the user details are returned from the cache. Otherwise, it
    queries the database to retrieve the user details and caches them for future use.

    Args:
        token (str, optional): The JWT token for authentication. Defaults to Depends(oauth2_scheme).

    Returns:
        dict: The user details.

    Raises:
        HTTPException: If the token is invalid or the user is not found in the database.
    """
    # Decode the token and extract the email
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    email: EmailStr = payload.get("sub")
    
    # Check if user exists in cache
    cached_user = redis_client.get(email)
    print("cached_user", cached_user)
    
    if cached_user:
        # Return user details from cache
        return json.loads(cached_user)
    
    # Query the database to retrieve user details
    user = await user_collection.find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Cache the user details for future use
    redis_client.set(email, json.dumps(user, default=str))
    
    return user

#search user with username
@router.get("/users/search", response_model=List[UserResponseModel])
async def search_users(
    query: str = Query(..., min_length=3),
    current_user: dict = Depends(get_current_user)
):
    users = await user_collection.find({"username": {"$regex": query, "$options": "i"}}).to_list(None)
    return users

#follow
@router.post("/users/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def follow_user(
    username: str,
    current_user: dict = Depends(get_current_user)
):
    if username == current_user["username"]:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")

    user_to_follow = await user_collection.find_one({"username": username})
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User not found")

    follow = await follow_collection.find_one({"follower_id": current_user["_id"], "following_id": user_to_follow["_id"]})
    if not follow:
        follow_data = FollowModel(follower_id=str(current_user["_id"]), following_id=str(user_to_follow["_id"]))
        await follow_collection.insert_one(follow_data.model_dump())
    return {"detail": "User followed"}

@router.post("/users/{username}/unfollow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user(
    username: str,
    current_user: dict = Depends(get_current_user)
):
    if username == current_user["username"]:
        raise HTTPException(status_code=400, detail="You cannot unfollow yourself")

    user_to_unfollow = await user_collection.find_one({"username": username})
    if not user_to_unfollow:
        raise HTTPException(status_code=404, detail="User not found")

    follow = await follow_collection.find_one({"follower_id": current_user["_id"], "following_id": user_to_unfollow["_id"]})
    if follow:
        await follow_collection.delete_one({"_id": follow["_id"]})
    return {"detail": "User unfollowed"}

