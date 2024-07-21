import os
import motor.motor_asyncio
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# MongoDB connection string
MONGO_DETAILS = os.getenv("MONGO_DETAILS")

if not MONGO_DETAILS:
    raise ValueError("MONGO_DETAILS environment variable is not set")

try:
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
    database = client.BlogBook

    # Verify the connection by listing databases
    # async def verify_connection():
    #     try:
    #         await client.server_info()  # This will raise an exception if the connection is not established 
    #         print("Connected to MongoDB")
    #     except Exception as e:
    #         print(f"Error connecting to MongoDB: {e}")
    #         raise

    # # Run the verification
    # import asyncio
    # asyncio.run(verify_connection())

    # Initialize collections
    user_collection = database.get_collection("users")
    discussion_collection = database.get_collection("discussions")
    comment_collection = database.get_collection("comments")
    like_collection = database.get_collection("likes")
    hashtag_collection = database.get_collection("hashtags")
    follow_collection = database.get_collection("follows")


    # print(user_collection, "user_collection")
    # print(discussion_collection, "discussion_collection")

except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    raise
