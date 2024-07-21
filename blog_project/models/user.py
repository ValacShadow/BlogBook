from bson import ObjectId

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class UserModel(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()))
    name: str
    username: str
    mobile_no: str
    email: EmailStr
    password: str
    liked_discussions: List[str] = []
    liked_comments: List[str] = []


class UserResponseModel(BaseModel):
    id: Optional[str]
    name: str
    mobile_no: str
    email: EmailStr

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[EmailStr] = None
