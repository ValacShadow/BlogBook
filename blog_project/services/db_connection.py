import dns
import os

import motor.motor_asyncio

# MongoDB connection string
MONGO_DETAILS = os.getenv("MONGO_DETAILS")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.BlogBook

user_collection = database.get_collection("users")
discussion_collection = database.get_collection("discussions")

# print(user_collection, "user_collection")