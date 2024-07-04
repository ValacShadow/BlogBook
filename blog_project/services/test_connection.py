from pymongo import MongoClient

MONGO_DETAILS = "mongodb://localhost:27017"

try:
    client = MongoClient(MONGO_DETAILS)
    db = client.BlogBook
    try:
        db.command("ping")
    except Exception as e:
        print(f"Error: {e}")
    # db.command("ping")
    print("Connected to MongoDB")
except Exception as e:
    print(f"Error: {e}")
