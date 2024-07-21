import motor.motor_asyncio
import asyncio
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# MongoDB connection string
MONGO_DETAILS = "mongodb+srv://sainivk565:nApRDjUAvYIiR1ut@cluster0.5kpc6rf.mongodb.net/?retryWrites=true&w=majority&tls=true&appName=Cluster0"

# Create MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client['BlogBook']
user_collection = database['users']
discussion_collection = database['discussions']

# Function to test inserting a document into the users collection
async def test_insert_user():
    try:
        user = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "securepassword"
        }
        result = await user_collection.insert_one(user)
        print(f"User inserted with ID: {result.inserted_id}")
    except Exception as e:
        print("Error inserting user:", e)

# Function to test retrieving a document from the users collection
async def test_find_user():
    try:
        user = await user_collection.find_one({"email": "john.doe@example.com"})
        print("User found:", user)
    except Exception as e:
        print("Error finding user:", e)

# Run the tests
async def main():
    await test_insert_user()
    await test_find_user()

asyncio.run(main())
