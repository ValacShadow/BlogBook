# models/user.py
from pydantic import BaseModel, EmailStr, Field

class UserModel(BaseModel):
    name: str
    mobile_no: str
    email: EmailStr

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"