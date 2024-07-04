# api/users.py
from fastapi import APIRouter, HTTPException, Depends
from models.user import UserModel, UserLoginModel, Token
from services.db_connection import user_collection
from services.auth_service import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    decode_access_token
)
from services.redis_service import redis_client

from pydantic import EmailStr
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/signup", response_model=UserModel)
async def signup(user: UserModel):
    print("in signup")
    try:
        existing_user = await user_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        user.password = get_password_hash(user.password)
        await user_collection.insert_one(user.dict())
    except Exception as e:
        print(e)
    return user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserModel)
async def get_me(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    email: EmailStr = payload.get("sub")
    cached_user = redis_client.get(email)
    if cached_user:
        return cached_user
    user = await user_collection.find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    redis_client.set(email, user)
    return user
