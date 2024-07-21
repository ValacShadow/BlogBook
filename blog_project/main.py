# main.py
import uvicorn
from fastapi import FastAPI

from api import users, discussions, images
from services.db_connection import client  # Importing the client for proper shutdown

app = FastAPI()

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(discussions.router, prefix="/discussions", tags=["discussions"])
app.include_router(images.router, prefix="/images", tags=["images"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Properly close the MongoDB connection on shutdown
# @app.on_event("shutdown")
# async def shutdown_db_client():
#     client.close()

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
