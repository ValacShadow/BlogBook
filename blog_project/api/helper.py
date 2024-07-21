from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr


from services.auth_service import decode_access_token
from services.db_connection import user_collection


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    email: EmailStr = payload.get("sub")
    user = await user_collection.find_one({"email": email})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user