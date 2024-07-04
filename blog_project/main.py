# main.py
import uvicorn

from fastapi import FastAPI

from api import users, discussions, images


# from services.db_connection import user_collection, discussion_collection

app = FastAPI()

# import motor.motor_asyncio

# # MongoDB connection string
# MONGO_DETAILS = "mongodb+srv://sainivk565:nApRDjUAvYIiR1ut@cluster0.5kpc6rf.mongodb.net/?retryWrites=true&w=majority"

# client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

#routes
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(discussions.router, prefix="/discussions", tags=["discussions"])
app.include_router(images.router, prefix="/images", tags=["images"])

@app.get("/")
def read_root():
    return {"Hello": "World"}



if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)